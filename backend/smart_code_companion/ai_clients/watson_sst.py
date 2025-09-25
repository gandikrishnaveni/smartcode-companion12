# File: smart_code_companion/ai_clients/watson_stt.py
import os
import base64
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class WatsonSTTClient:
    def __init__(self):
        self.stt_api_key = os.getenv("IBM_STT_API_KEY")
        self.stt_url = os.getenv("IBM_STT_URL")

        if not all([self.stt_api_key, self.stt_url]):
            raise ValueError("IBM Watson Speech-to-Text credentials missing!")

        authenticator = IAMAuthenticator(self.stt_api_key)
        self.stt = SpeechToTextV1(authenticator=authenticator)
        self.stt.set_service_url(self.stt_url)

    def transcribe(self, audio_base64: str) -> str:
        try:
            audio_bytes = base64.b64decode(audio_base64)
            response = self.stt.recognize(
                audio=audio_bytes,
                content_type="audio/wav",   # adjust to your frontend recording format
                model="en-US_BroadbandModel"
            ).get_result()

            if "results" in response and response["results"]:
                return response["results"][0]["alternatives"][0]["transcript"].strip()
            return "No speech detected"
        except Exception as e:
            raise RuntimeError(f"Watson STT failed: {e}")
