# File: smart_code_companion/ai_clients/ibm.py
# Description: IBM Watson AI client for code comments, debugging, and documentation

import os
import base64
import time
from typing import List
from ibm_watsonx_ai.foundation_models import ModelInference
from smart_code_companion.core.config import get_settings
from smart_code_companion.ai_clients.base import AIClient
from smart_code_companion.core.models import SkillLevel


class IBMWatsonClient(AIClient):
    """
    IBM Watson AI client for:
    - Function-wise code comments
    - Speech-to-text comments
    - Debugging
    - Documentation generation
    Implements retry logic for rate-limit errors.
    """

    def __init__(self):
        settings = get_settings()
        self.apikey = settings.WATSONX_APIKEY or os.getenv("IBM_API_KEY")
        self.url = settings.WATSONX_URL or os.getenv("IBM_API_URL")
        self.project_id = settings.WATSONX_PROJECT_ID or os.getenv("IBM_PROJECT_ID")

        if not all([self.apikey, self.url, self.project_id]):
            raise ValueError(
                "IBM Watson credentials are missing! Check environment variables or settings."
            )

    def _call_ibm(self, prompt: str, max_tokens: int = 500, retries: int = 3, backoff: int = 2) -> str:
        """Call IBM WatsonX API with retry logic."""
        attempt = 0
        while attempt <= retries:
            try:
                model = ModelInference(
                    model_id="ibm/granite-3-3-8b-instruct",
                    params={"decoding_method": "greedy", "max_new_tokens": max_tokens},
                    credentials={"apikey": self.apikey, "url": self.url},
                    project_id=self.project_id,
                )
                result = model.generate_text(prompt=prompt)
                if isinstance(result, str):
                    return result
                return result.get("generated_text", str(result))
            except Exception as e:
                if "consumption_limit_reached" in str(e) and attempt < retries:
                    wait_time = backoff ** attempt
                    print(f"Rate limit reached. Retrying in {wait_time}s... (Attempt {attempt+1}/{retries})")
                    time.sleep(wait_time)
                    attempt += 1
                else:
                    raise RuntimeError(f"IBM WatsonX API call failed: {e}")
        raise RuntimeError("IBM WatsonX API call failed after multiple retries due to rate limits.")

    # ---------------- Function & Line Comments ----------------
    def get_comment(self, code: str, level: SkillLevel) -> str:
     """
     Returns code + AI comment together, ready for frontend display.
     """
     level_prompts = {
        "beginner": f"Explain this code concisely in 5 words max. Code:\n{code}",
        "intermediate": f"Explain this code in 3 words max. Code:\n{code}",
        "advanced": f"Explain this code in 1-2 words. Code:\n{code}"
     }
     lvl = level.lower() if level.lower() in level_prompts else "beginner"

     ai_output = self._call_ibm(level_prompts[lvl], max_tokens=50).strip()
     if not ai_output:
        ai_output = "No comment generated"

    # Append AI comment to the code itself
     code_lines = code.splitlines()
     comment_lines = ai_output.splitlines()

     annotated_lines = []
     for i, line in enumerate(code_lines):
        comment = comment_lines[i] if i < len(comment_lines) else ai_output
        annotated_lines.append(f"{line}  # {comment}")

     return "\n".join(annotated_lines)

    # ---------------- Documentation ----------------
    def get_documentation(self, code: str, level: SkillLevel = "beginner") -> str:
        level_prompts = {
            "beginner": "Write detailed documentation. Max 50 words per function.",
            "intermediate": "Write concise documentation. Max 25 words per function.",
            "advanced": "Write minimal documentation. Max 10 words per function."
        }
        lvl = level.lower() if level.lower() in level_prompts else "beginner"
        prompt = f"{level_prompts[lvl]}\n\nCode:\n{code}"
        max_tokens_map = {"beginner": 300, "intermediate": 200, "advanced": 100}
        return self._call_ibm(prompt, max_tokens=max_tokens_map.get(lvl, 300))

    # ---------------- Debugging ----------------
    def get_debug(self, code: str, level: SkillLevel = "beginner") -> str:
        """
        Generates AI-powered debugging explanation and fixed code.
        Returns a single string containing:
         - Error
         - Explanation
         - Suggestion / Corrected Code
        """
        level_prompts = {
            "beginner": "Analyze this code, explain the first error in detail for a beginner. Show corrected code in 15-20 words.",
            "intermediate": "Analyze this code, explain the first error concisely. Show corrected code in 7-10 words.",
            "advanced": "Analyze this code, give minimal hints for the first error. Show corrected code in 7 or fewer words."
        }
        lvl = level.lower() if level.lower() in level_prompts else "beginner"
        prompt = f"{level_prompts[lvl]}\n\nCode:\n{code}"
        max_tokens_map = {"beginner": 300, "intermediate": 200, "advanced": 100}
        ai_output = self._call_ibm(prompt, max_tokens=max_tokens_map.get(lvl, 300))
        return ai_output.strip()

    # ---------------- Speech-to-text ----------------
    def transcribe_audio(self, audio_base64: str) -> str:
        try:
            audio_bytes = base64.b64decode(audio_base64)
            truncated_bytes = audio_bytes[:1000]
            prompt = f"Transcribe the following audio (in bytes) into text:\n{truncated_bytes}..."
            return self._call_ibm(prompt, max_tokens=300)
        except Exception as e:
            raise RuntimeError(f"Speech-to-text failed: {e}")
