from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")


async def send_notification_email(email: str, content: str, reason: str):
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=email,
            subject="Your Comment Has Been Flagged",
            html_content=f"""
            <h2>Content Moderation Notification</h2>
            <p>Dear User,</p>
            <p>Your comment has been flagged by our content moderation system.</p>
            <p><strong>Comment:</strong> "{content}"</p>
            <p><strong>Reason:</strong> {reason}</p>
            <p>This comment will be reviewed by our moderation team.</p>
            <br>
            <p>Best regards,<br>Content Moderation Team</p>
            """,
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return True

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
