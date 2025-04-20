from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from moderation import models, schemas
from moderation.database import get_db, engine
from moderation.moderation import ContentModerator
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from moderation.email_utils import send_notification_email

# Create tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Content Moderation API",
    description="A microservice for moderating user-generated content using AI",
)

# Security
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
moderator = ContentModerator()


# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# Routes
@app.post("/register", response_model=schemas.User, tags=["Authentication"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = (
        db.query(models.User)
        .filter(
            models.User.email == user.email or models.User.username == user.username
        )
        .first()
    )
    if db_user:
        raise HTTPException(
            status_code=400, detail="Email/Username already registered!!"
        )

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email, username=user.username, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/comments/", response_model=schemas.Comment, tags=["Comments"])
async def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Initial profanity check
    if any(word in comment.content.lower() for word in ["fuck", "shit", "damn"]):
        try:
            # Send email notification
            await send_notification_email(
                current_user.email,
                comment.content,
                "Your comment couldn't be posted as it contains inappropriate language",
            )
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment contains inappropriate language",
        )

    new_comment = models.Comment(
        content=comment.content, user_id=current_user.id, status="pending"
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # Check content using AI moderation
    is_flagged, reason = await moderator.moderate_content(comment.content)

    if is_flagged:
        new_comment.status = "flagged"
        flagged_comment = models.FlaggedComment(
            comment_id=new_comment.id, user_id=current_user.id, reason=reason
        )
        db.add(flagged_comment)
        db.commit()

        try:
            # Send email notification
            await send_notification_email(current_user.email, comment.content, reason)
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Comment has been flagged for moderation. Reason: {reason}",
        )

    new_comment.status = "approved"
    db.commit()

    return new_comment


@app.get("/comments/", response_model=list[schemas.Comment], tags=["Comments"])
def get_comments(db: Session = Depends(get_db)):
    return db.query(models.Comment).all()


@app.get("/comments/flagged", response_model=list[schemas.Comment], tags=["Comments"])
def get_flagged_comments(db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.status == "flagged").all()


@app.get("/comments/approved", response_model=list[schemas.Comment], tags=["Comments"])
def get_approved_comments(db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.status == "approved").all()


@app.get("/analytics/comments", tags=["Analytics"])
async def get_comment_analytics(db: Session = Depends(get_db)):
    total_comments = db.query(models.Comment).count()
    flagged_comments = (
        db.query(models.Comment).filter(models.Comment.status == "flagged").count()
    )
    approved_comments = (
        db.query(models.Comment).filter(models.Comment.status == "approved").count()
    )

    return {
        "total_comments": total_comments,
        "flagged_comments": flagged_comments,
        "approved_comments": approved_comments,
        "flagged_percentage": (
            (flagged_comments / total_comments) * 100 if total_comments > 0 else 0
        ),
    }
