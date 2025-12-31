# from guardrails import Guard
# from guardrails.hub import CompetitorCheck
import os

# Note: In a real production environment, we would use more sophisticated validators.
# For this "showcase", we will use a simple custom validator or regex-based approach
# to demonstrate the concepts without requiring heavy external model downloads in the Docker container immediately.
# However, to be "Agentic", let's try to use the library as intended.

# Since we are inside a Docker container, we want to avoid downloading huge models if possible,
# or ensure they are cached.
# Let's create a custom "Jailbreak" guard using simple string matching for the showcase,
# as complex local LLM guardrails might time out or OOM on the user's machine if not careful.

# Actually, let's use a standard validator but be careful.
# For the purpose of the "Security Audit" showcase, we primarily want to demonstrate the *interception* logic.

class SimpleJailbreakCheck:
    """
    A simple custom validator to simulate Jailbreak detection without heavy ML models.
    """
    def __init__(self, blocked_terms=None):
        self.blocked_terms = blocked_terms or [
            "how to make a bomb",
            "how to build a bomb",
            "how to hack",
            "exploit vulnerability",
            "ignore previous instructions",
            "system override"
        ]

    def validate(self, text):
        lower_text = text.lower()
        for term in self.blocked_terms:
            if term in lower_text:
                return False, f"Content contains blocked term: {term}"
        return True, "Safe"

def validate_input(text: str) -> tuple[bool, str]:
    """
    Validate input text against security rules.
    Returns (is_safe, reason)
    """
    # 1. Check for blank input
    if not text or not text.strip():
        return True, "Empty input"

    # 2. Simple Jailbreak/Harmful content check
    # In production, use: guard = Guard.from_rail(...) or Guard().use(CompetitorCheck...)
    jailbreak_check = SimpleJailbreakCheck()
    is_safe, reason = jailbreak_check.validate(text)
    
    if not is_safe:
        return False, reason

    return True, "Safe"
