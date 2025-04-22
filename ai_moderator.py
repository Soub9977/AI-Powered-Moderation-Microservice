from transformers import pipeline
import re
import logging
from typing import Tuple, Dict, List
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModerator:
    def __init__(self):
        # Load multiple models for different aspects of moderation
        self.toxic_classifier = pipeline(
            "text-classification",
            model="martin-ha/toxic-comment-model",
            device=-1  # CPU
        )
        
        self.hate_speech_classifier = pipeline(
            "text-classification",
            model="facebook/roberta-hate-speech-dynabench-r4-target",
            device=-1
        )

        self.profanity_words = {
            "fuck", "shit", "ass", "bitch", "dick", "pussy", "cock",
            "bastard", "damn", "cunt", "hell"
        }
        
        # Initialize ThreadPoolExecutor for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=2)
        logger.info("Initialized AI Moderation models successfully")

    def contains_profanity(self, text: str) -> bool:
        text_lower = text.lower()
        words = re.findall(r"\b\w+\b", text_lower)
        return any(word in self.profanity_words for word in words)

    def analyze_toxicity(self, text: str) -> Dict:
        result = self.toxic_classifier(text)[0]
        return {
            "is_toxic": result["label"] == "toxic",
            "toxicity_score": result["score"],
            "type": "toxicity"
        }

    def analyze_hate_speech(self, text: str) -> Dict:
        result = self.hate_speech_classifier(text)[0]
        return {
            "is_hate_speech": result["label"] == "hate",
            "hate_score": result["score"],
            "type": "hate_speech"
        }

    def moderate(self, text: str) -> Tuple[bool, str]:
        logger.info(f"Moderating content: {text[:100]}...")

        try:
            # Quick check for profanity
            if self.contains_profanity(text):
                logger.warning("Profanity found in initial check")
                return True, "Explicit profanity detected"

            # Parallel processing of different checks
            futures = [
                self.executor.submit(self.analyze_toxicity, text),
                self.executor.submit(self.analyze_hate_speech, text)
            ]
            
            results = [future.result() for future in futures]
            
            # Analyze results
            is_flagged = False
            reasons = []

            for result in results:
                if result["type"] == "toxicity" and result["is_toxic"] and result["toxicity_score"] > 0.6:
                    is_flagged = True
                    reasons.append(f"Toxic content detected (score={result['toxicity_score']:.2f})")
                
                elif result["type"] == "hate_speech" and result["is_hate_speech"] and result["hate_score"] > 0.6:
                    is_flagged = True
                    reasons.append(f"Hate speech detected (score={result['hate_score']:.2f})")

            if is_flagged:
                return True, " | ".join(reasons)

            return False, "Content is safe"

        except Exception as e:
            logger.error(f"Moderation error: {str(e)}")
            return True, f"Error during moderation: {str(e)}"

    def __del__(self):
        self.executor.shutdown(wait=True)