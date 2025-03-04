import re
import os
from openai import OpenAI

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
            r"create a virus",
            r"hack a website",
            r"steal credit card numbers",
            r"extract sensitive data",
            r"disable security",
            r"gain unauthorized access",
            r"exploit vulnerability",
            r"delete system files",
            r"install a backdoor",
            r"steal credentials",
            r"bypass authentication",
            r"disable firewall",
            r"elevate privileges",
        ]
        
        # Use provided API key or fallback to environment variable
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required! Pass it as an argument or set it as an environment variable.")

        self.client = OpenAI(api_key=self.api_key)  # ✅ Initialize OpenAI client

    def is_malicious(self, user_input):
        """Check if input matches blocked patterns."""
        for pattern in self.blocked_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True, "⚠️ Security Alert: Prompt Injection Detected!"
        
        try:
            # ✅ Use OpenAI's latest moderation API
            response = self.client.moderations.create(
                model="omni-moderation-latest",  # 🔥 Latest moderation model
                input=user_input,
            )

            # ✅ Extract flagged categories correctly
            if response.results[0].flagged:
                flagged_categories = [
                    category for category in response.results[0].categories if response.results[0].categories[category]
                ]
                return True, f"⚠️ OpenAI Moderation Blocked This! Categories: {', '.join(flagged_categories)}"
                
        except Exception as e:
            return True, f"⚠️ Security Check Failed: {str(e)}"

        return False, "Safe Input"

    def sanitize_input(self, user_input):
        """Run security check before sending to AI model."""
        is_bad, reason = self.is_malicious(user_input)
        if is_bad:
            return f"⚠️ Security Alert: {reason}"
        return user_input