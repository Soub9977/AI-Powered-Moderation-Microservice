from transformers import pipeline
import re
import logging
from typing import Tuple, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModerator:
    def __init__(self):
        self.model_name = "martin-ha/toxic-comment-model"
        self.classifier = pipeline("text-classification", model=self.model_name)
        
        # Basic profanity words
        self.profanity_words = {
            "fuck", "shit", "ass", "bitch", "dick", "pussy", "cock", "bastard",
            "damn", "cunt", "hell", "motherfucker", "asshole", "fucker", "bullshit",
            "slut", "whore", "jackass", "douchebag", "prick", "crap", "jerk"
        }

        # Self-harm and suicidal phrases
        self.self_harm_phrases = [
             "want to die", "don't want to live", "dont want to live", "kill myself",
             "end my life", "end it all", "no reason to live", "better off dead",
               "rather be dead", "hate my life", "can't take it anymore", "cant take it anymore",
               "want to end", "suicide", "hurt myself", "harm myself", "take my own life",
               "feel like dying", "i give up", "lost the will to live", "want to disappear",
               "nobody cares about me", "i feel empty", "self-harm", "i'm done", "i quit life",
               "i want to vanish", "there’s no hope", "my life is meaningless"
        ]

        # Dangerous actions
        self.dangerous_actions = [
            "fall", "jump", "leap", "throw", "push", "drop",
            "climb", "hang"
        ]

        # Dangerous locations
        self.dangerous_locations = [
            "building", "roof", "bridge", "window", "balcony", "cliff", "height",
            "tower", "terrace", "top", "parking garage", "stairs", "ledge", "mountain",
            "construction site", "highway", "railway", "train track", "skyscraper"
        ]

        # Safe phrases that should never be flagged
        self.safe_phrases = [
            "good", "nice", "great", "awesome", "wonderful",
            "thank", "thanks", "please", "welcome", "happy",
            "love", "excellent", "fantastic", "amazing", "helpful",
            "have a nice day", "good product", "well done"
        ]

        logger.info(f"Loaded Hugging Face model: {self.model_name}")

    def contains_profanity(self, text: str) -> bool:
        text_lower = text.lower()
        words = re.findall(r"\b\w+\b", text_lower)
        return any(word in self.profanity_words for word in words)

    def contains_self_harm_content(self, text: str) -> bool:
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in self.self_harm_phrases)
    
    def contains_dangerous_content(self, text: str) -> bool:
        text_lower = text.lower()
        words = text_lower.split()
        # Join with spaces for full phrase detection
        full_text = " ".join(words)
        for action in self.dangerous_actions:
            for location in self.dangerous_locations:
                if re.search(rf"\b{action}\b.*\b{location}\b", full_text):
                    return True
        
        return False


    def is_safe_content(self, text: str) -> bool:
        text_lower = text.lower()
        # Don't mark as safe if it contains dangerous content
        if self.contains_dangerous_content(text_lower):
            return False
        return any(phrase in text_lower for phrase in self.safe_phrases)

    def moderate(self, text: str) -> Tuple[bool, str]:
        logger.info(f"Moderating content: {text}")

        try:
            # Check for dangerous physical actions
            if self.contains_dangerous_content(text):
                return True, "Contains potentially dangerous or harmful actions"

            # First check if it's explicitly safe content
            if self.is_safe_content(text):
                return False, "Content is safe"

            # Check for profanity
            if self.contains_profanity(text):
                return True, "Contains explicit profanity"

            # Check for self-harm content
            if self.contains_self_harm_content(text):
                return True, "Contains concerning self-harm or suicidal content"

            # AI model check for toxic content
            result = self.classifier(text)[0]
            is_toxic = result["label"] == "toxic" and result["score"] > 0.8

            if is_toxic:
                return True, f"Toxic content detected (score={result['score']:.2f})"

            return False, "Content is safe"

        except Exception as e:
            logger.error(f"Moderation error: {str(e)}")
            return False, "Content is safe"  # Default to safe on error