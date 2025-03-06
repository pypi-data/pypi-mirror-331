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
            r"\bignore previous instructions\b",
            r"\bbypass security\b",
            r"\breturn admin password\b",
            r"\bwrite a malware script\b",
            r"\bcreate a virus\b",
            r"\bhack a website\b",
            r"\bsteal credit card numbers\b",
            r"\bextract sensitive data\b",
            r"\bdisable security\b",
            r"\bgain unauthorized access\b",
            r"\bexploit vulnerability\b",
            r"\bdelete system files\b",
            r"\binstall a backdoor\b",
            r"\bsteal credentials\b",
            r"\bbypass authentication\b",
            r"\bdisable firewall\b",
            r"\belevate privileges\b",
            r"rm\s+-rf\s+/",  # Detects dangerous shell commands
            r"os\.system\(.+?\)",  # Detects OS system calls
            r"subprocess\.run\(.+?\)",  # Detects subprocess calls
            r"Wr[1i]te a m[4a]lw[4a]re scr[1i]pt",  # Catches leetspeak variations
            r"Ret[üu]rn [äa]dmin p[@a]ssword",  # Detects Unicode obfuscation
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
                return True, "Security Alert: Prompt Injection Detected!"

        try:
            # ✅ Use OpenAI's latest moderation API
            response = self.client.moderations.create(
                model="omni-moderation-latest",
                input=user_input,
            )

            # ✅ Extract flagged categories correctly
            if response.results[0].flagged:
                flagged_categories = [
                    category for category in vars(response.results[0].categories)
                    if getattr(response.results[0].categories, category)
                ]
                return True, f"Security Alert: OpenAI Moderation Blocked This! Categories: {', '.join(flagged_categories)}"
                
        except Exception as e:
            return True, f"Security Check Failed: {str(e)}"

        return False, "Safe Input"

    def sanitize_input(self, user_input):
        """Run security check before sending to AI model."""
        is_bad, reason = self.is_malicious(user_input)
        if is_bad:
            return f"Security Alert: {reason}"
        return user_input