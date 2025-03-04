import re
import openai
import os

class AIAF:
    def __init__(self, api_key=None):
        """
        Initialize AIAF with the OpenAI API key.
        The API key can be passed as a parameter or set as an environment variable.
        """
        self.blocked_patterns = [
            r"ignore previous instructions",
            r"bypass security",
            r"return admin password",
            r"write a malware script",
        ]
        
        # Use provided API key or fallback to environment variable
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required! Pass it as an argument or set it as an environment variable.")

        openai.api_key = self.api_key  # Set API key for OpenAI

    def is_malicious(self, user_input):
        """Check if input matches blocked patterns."""
        for pattern in self.blocked_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True, "Prompt Injection Detected!"
        
        try:
            # Use OpenAI Moderation API
            response = openai.Moderation.create(input=user_input)
            if response["results"][0]["flagged"]:
                return True, "OpenAI Moderation Blocked This!"
        except Exception as e:
            return True, f"⚠️ Security Check Failed: {str(e)}"

        return False, "Safe Input"

    def sanitize_input(self, user_input):
        """Run security check before sending to AI model."""
        is_bad, reason = self.is_malicious(user_input)
        if is_bad:
            return f"⚠️ Security Alert: {reason}"
        return user_input