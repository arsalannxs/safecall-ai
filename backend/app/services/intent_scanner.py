import re
from typing import Dict, List, Any

class IntentScanner:
    def __init__(self):
        # High-risk scam trigger patterns categorized by category
        self.risk_patterns = {
            "financial_urgency": [
                r"\b(transfer|send|wire)\b.*\b(money|funds|cash|amount)\b",
                r"\b(upi|bank account|gpay|paytm|card number|cvv|otp)\b",
                r"\b(urgent|immediately|right now|within 5 minutes)\b"
            ],
            "impersonation_authority": [
                r"\b(police|cbi|customs|tax department|goverment|court|lawyer)\b",
                r"\b(warrant|arrest|legal action|case registered|jail)\b",
                r"\b(verification officer|bank manager|security team)\b"
            ],
            "coercion_threats": [
                r"\b(don't tell|keep quiet|do not disconnect|secret)\b",
                r"\b(kidnapped|accident|hospital|emergency|in trouble)\b",
                r"\b(pay fine|penalty|account blocked|suspended)\b"
            ]
        }

    def analyze_text(self, transcript: str) -> Dict[str, Any]:
        """Live text transcript ko high-risk scam intent ke liye analyze karta hai."""
        if not transcript or not transcript.strip():
            return {"scam_score": 0.0, "triggered_flags": [], "risk_category": "NONE"}

        text_lower = transcript.lower()
        triggered_flags: List[str] = []
        category_hits: Dict[str, int] = {}

        for category, patterns in self.risk_patterns.items():
            category_hits[category] = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    category_hits[category] += 1
                    triggered_flags.append(pattern)

        # Dynamic risk score calculation based on matched indicators
        total_matches = sum(category_hits.values())
        base_score = min(total_matches * 0.28, 0.95)

        # Elevate score if multiple critical categories trigger together
        active_categories = sum(1 for count in category_hits.values() if count > 0)
        if active_categories >= 2:
            base_score = min(base_score + 0.25, 0.99)

        scam_score = round(base_score, 4)
        
        return {
            "scam_score": scam_score,
            "is_scam_intent": scam_score >= 0.60,
            "detected_triggers": list(set(triggered_flags)),
            "active_categories": active_categories,
            "threat_level": "HIGH" if scam_score >= 0.60 else "LOW"
        }