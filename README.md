AI-Powered Content Moderation API

A FastAPI-based microservice that provides AI-powered content moderation for user-generated content. This service helps maintain content quality by automatically detecting and flagging inappropriate content using AI/ML techniques.

Features

- AI-Powered Content Moderation: Automatically detect and flag inappropriate content
- User Authentication: Secure JWT-based authentication system
- Comment Management: Create, retrieve, and moderate comments
- Email Notifications: Automatic notifications for flagged content
- Analytics: Track moderation statistics and metrics
- API Documentation: Interactive API documentation with Swagger UI

Quick Start

Prerequisites:
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL

Installation:

1. Clone the repository:
git clone (https://github.com/Soub9977/AI-Powered-Moderation-Microservice)
cd ai-powered-moderation

2. Create a .env file:
DATABASE_URL=postgresql://user:password@db:5432/moderation
SECRET_KEY=your-secret-key
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-password

3. Build and run with Docker Compose:
docker-compose up --build

The API will be available at http://localhost:8000

API Documentation

Once the service is running, you can access:
- Swagger UI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

Key Endpoints:
- POST /register: Register a new user
- POST /token: Get access token
- POST /comments/: Create a new comment
- GET /comments/: Get all comments
- GET /comments/flagged: Get flagged comments
- GET /comments/approved: Get approved comments
- GET /analytics/comments: Get comment moderation analytics

Development Setup

1. Create a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Install dependencies:
pip install -r requirements.txt

3. Run the development server:
uvicorn moderation.main:app --reload

Project Structure

moderation/
├── __init__.py
├── main.py              # FastAPI application and routes
├── content_moderator.py # AI moderation logic
├── database.py         # Database configuration
├── models.py           # SQLAlchemy models
├── schemas.py          # Pydantic schemas
└── email_utils.py      # Email notification utilities

Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Rate limiting
- Security headers
- Input validation
- Error handling

Analytics and Monitoring

The service provides basic analytics through the /analytics/comments endpoint:
- Total comments processed
- Number of flagged comments
- Number of approved comments
- Flagging rate percentage

Docker Support

The project includes Docker support for easy deployment:
- Multi-stage builds for optimal image size
- Docker Compose for orchestration
- PostgreSQL database container
- Environment variable configuration

Testing

Run the test suite:
pytest

Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request




Acknowledgments

- FastAPI framework
- SQLAlchemy
- Python-Jose
- Passlib
- Other open-source contributors




Future Improvements

- Enhanced AI moderation algorithms
- Real-time moderation websocket support
- Multi-language support
- Content categorization
- User reputation system
- Batch processing capabilities
- Advanced analytics dashboard

Requirements

Create a requirements.txt file with these dependencies:
fastapi
uvicorn
sqlalchemy
passlib
python-jose[cryptography]
python-multipart
psycopg2-binary
bcrypt
aiosmtplib
python-dotenv
prometheus-client
pytest
httpx

Environment Variables

Make sure to set up these environment variables:
- DATABASE_URL
- SECRET_KEY
- SMTP_HOST
- SMTP_PORT
- SMTP_USERNAME
- SMTP_PASSWORD

API Usage Examples

1. Register a new user:
curl -X POST "http://localhost:8000/register" \
-H "Content-Type: application/json" \
-d '{"email": "test@example.com", "username": "testuser", "password": "password123"}'

2. Get access token:
curl -X POST "http://localhost:8000/token" \
-H "Content-Type: application/form-data" \
-d "username=testuser&password=password123"

3. Create a comment:
curl -X POST "http://localhost:8000/comments/" \
-H "Authorization: Bearer <your_token>" \
-H "Content-Type: application/json" \
-d '{"content": "This is a test comment"}'

