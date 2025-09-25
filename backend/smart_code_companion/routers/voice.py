# File: smart_code_companion/api/routes/voice.py
import base64
import io
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from smart_code_companion.core.config import get_settings
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pydub import AudioSegment

router = APIRouter()


# --- Request model ---
class VoiceCommentRequest(BaseModel):
    audio_base64: str
    code: str
    level: str


# --- Helper: get Watson client ---
def get_watson_stt():
    settings = get_settings()
    if not settings.IBM_STT_API_KEY or not settings.IBM_STT_URL:
        raise HTTPException(status_code=500, detail="IBM Watson STT credentials missing")

    authenticator = IAMAuthenticator(settings.IBM_STT_API_KEY)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(settings.IBM_STT_URL)
    return stt


# --- Voice route ---
@router.post("/voice-comment")
async def voice_comment(req: VoiceCommentRequest):
    try:
        # Decode base64 → bytes
        audio_bytes = base64.b64decode(req.audio_base64)

        # Reject too-short audio early
        if len(audio_bytes) < 1000:
            raise HTTPException(status_code=400, detail="Recording too short or silent. Try again!")

        # Convert webm/ogg → WAV using pydub
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")  # or "ogg"
        except Exception:
            # Fallback: try wav directly
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")

        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_bytes = wav_io.getvalue()

        # Send to Watson STT
        stt = get_watson_stt()
        try:
            result = stt.recognize(
                audio=wav_bytes,
                content_type="audio/wav",
                model="en-US_BroadbandModel"
            ).get_result()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Watson STT failed: {e}")

        # Extract transcription
        if result.get("results"):
            text = result["results"][0]["alternatives"][0]["transcript"].strip()
        else:
            text = "(no speech detected)"

        # Return transcription
        return {
            "voice_comment": text,
            "commented_code": f"{req.code}\n# Voice Instruction: {text}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice comment failed: {e}")
