from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "google")  # "google" or "ibm"

app = FastAPI()

# ===== GOOGLE GEMINI SETUP =====
if MODEL_PROVIDER == "google":
    try:
        from google.generativeai import client as gclient
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        gclient.configure(api_key=GOOGLE_API_KEY)
    except ImportError:
        raise ImportError(
            "google-generativeai package not installed. Run `pip install google-generativeai`"
        )

# ===== IBM WATSONX SETUP =====
if MODEL_PROVIDER == "ibm":
    try:
        from ibm_watsonx_ai.foundation_models import Model
        WATSONX_APIKEY = os.getenv("WATSONX_APIKEY")
        WATSONX_URL = os.getenv("WATSONX_URL")
        WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
    except ImportError:
        raise ImportError(
            "ibm-watsonx-ai package not installed. Run `pip install ibm-watsonx-ai`"
        )

# Request model
class CommentRequest(BaseModel):
    code: str
    level: str = "intermediate"

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "provider": MODEL_PROVIDER}

# Commenting endpoint
@app.post("/comment")
async def comment(req: CommentRequest):
    prompt = f"Add {req.level} level comments to this Java code:\n{req.code}"

    try:
        if MODEL_PROVIDER == "google":
            # New Google Generative AI API
            response = gclient.text.generate(
                model="gemini-1.5",
                prompt=prompt,
                max_output_tokens=500
            )
            # response is a dict with 'candidates' list
            commented_code = response['candidates'][0]['content']
            return {"commented_code": commented_code}

        elif MODEL_PROVIDER == "ibm":
            model = Model(
                model_id="ibm/granite-13b-chat-v2",
                params={"decoding_method": "greedy", "max_new_tokens": 500},
                credentials={"apikey": WATSONX_APIKEY, "url": WATSONX_URL},
                project_id=WATSONX_PROJECT_ID
            )
            result = model.generate_text(prompt=prompt)
            return {"commented_code": result}

        else:
            raise ValueError("Unsupported MODEL_PROVIDER")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

