import requests
from typing import Tuple
import os
import re
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentModerator:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = os.getenv("OPENROUTER_API_URL")
        self.model = os.getenv("MODEL_NAME")

        # Log initialization
        logger.info(f"ContentModerator initialized with:")
        logger.info(f"API URL: {self.api_url}")
        logger.info(f"Model: {self.model}")

        self.profanity_words = {
            "fuck",
            "shit",
            "ass",
            "bitch",
            "dick",
            "pussy",
            "cock",
            "bastard",
            "damn",
            "cunt",
            "hell",
        }

    async def test_connection(self) -> bool:
        """Test the connection to OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "Content-Type": "application/json",
        }

        test_data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a content moderator."},
                {"role": "user", "content": "Hello, this is a test."},
            ],
        }

        try:
            logger.info("Testing connection to OpenRouter API...")
            response = requests.post(self.api_url, headers=headers, json=test_data)

            logger.info(f"Response status code: {response.status_code}")
            logger.info(
                f"Response content: {response.text[:200]}..."
            )  # Log first 200 chars

            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    def contains_profanity(self, text: str) -> bool:
        text_lower = text.lower()
        words = re.findall(r"\b\w+\b", text_lower)
        return any(word in self.profanity_words for word in words)

    async def moderate_content(self, text: str) -> Tuple[bool, str]:
        logger.info(f"Moderating content: {text}")

        if self.contains_profanity(text):
            logger.info("Profanity detected in initial check")
            return True, "Content contains explicit profanity"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "Content-Type": "application/json",
        }

        prompt = f"""
        Strictly analyze this content for:
        1. Profanity or swear words
        2. Hate speech or discrimination
        3. Threats or violence
        4. Sexual content
        5. Harassment or bullying
        6. Offensive language
        7. Personal attacks
        
        Respond ONLY with:
        'FLAGGED: <specific reason>' if ANY of the above are found
        'SAFE' if the content is completely appropriate
        
        Content to analyze: "{text}"
        """

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a strict content moderation AI. Flag ANY inappropriate content.",
                },
                {"role": "user", "content": prompt},
            ],
        }

        try:
            logger.info("Sending request to OpenRouter API...")
            response = requests.post(self.api_url, headers=headers, json=data)

            logger.info(f"API Response Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                logger.info(f"API Response: {result}")

                response_text = (
                    result["choices"][0]["message"]["content"].strip().lower()
                )
                logger.info(f"Moderation result: {response_text}")

                if "safe" not in response_text:
                    return True, "Content may be inappropriate"

                if response_text.startswith("flagged:"):
                    reason = response_text[8:].strip()
                    return True, reason

                if any(word in text.lower() for word in ["fuck", "shit", "damn"]):
                    return True, "Content contains offensive language"

                return False, ""

            else:
                logger.error(f"API Error: {response.status_code}")
                logger.error(f"Error response: {response.text}")
                return True, "Error in moderation service - flagging for manual review"

        except Exception as e:
            logger.error(f"Moderation error: {str(e)}")
            return True, "Error in moderation service - flagging for manual review"
