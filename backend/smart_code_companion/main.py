# File: smart_code_companion/main.py
# Description: Entry point for Smart Code Companion FastAPI backend

import sys
import os
import io

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from smart_code_companion.core.config import get_settings
from smart_code_companion.core.models import (
    CodeRequest,
    CommentResponse,
    HealthResponse,
    DebugRequest,
    DebugResponse,
)
from smart_code_companion.ai_clients.base import AIClient
from smart_code_companion.ai_clients.client import get_ai_client
from smart_code_companion.routers import comment, run, debug, docs,voice

# ==============================================================================
# PATH FIX (ensures project modules are importable)
# ==============================================================================
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ==============================================================================
# App Initialization
# ==============================================================================
settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    description="A smart assistant to provide feedback on your code, powered by AI.",
    version="1.0.0",
)

# Allow all origins (development convenience)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Root & Health
# ==============================================================================
@app.get("/", tags=["Root"], include_in_schema=False)
def read_root():
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "docs_url": "/docs",
        "health_check": f"{settings.API_V1_STR}/health",
    }


@app.get(
    f"{settings.API_V1_STR}/health",
    response_model=HealthResponse,
    tags=["Monitoring"],
    summary="Check Service Health",
)
def health_check():
    return HealthResponse(status="ok")

# ==============================================================================
# Native Code Execution (Python only for now)
# ==============================================================================
@app.post(f"{settings.API_V1_STR}/run-code")
def run_code(request: CodeRequest):
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()

    try:
        exec(request.code, {})  # run in empty scope
        output = mystdout.getvalue()
        return {
            "error": None,
            "output": output.strip(),
            "fixed_code": request.code,
        }
    except Exception as e:
        return {
            "error": str(e),
            "output": None,
            "fixed_code": request.code,
        }
    finally:
        sys.stdout = old_stdout

# ==============================================================================
# AI Endpoints (Comment, Debug)
# ==============================================================================
@app.post(
    f"{settings.API_V1_STR}/comment",
    response_model=CommentResponse,
    tags=["AI"],
    summary="Get AI-Powered Code Feedback",
)
def get_code_comment(
    request: CodeRequest, ai_client: AIClient = Depends(get_ai_client)
) -> CommentResponse:
    try:
        comment = ai_client.get_comment(code=request.code, level=request.level)
        return CommentResponse(comment=comment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI provider error: {e}",
        )


@app.post(
    f"{settings.API_V1_STR}/debug",
    response_model=DebugResponse,
    tags=["AI"],
    summary="Get AI-Powered Debugging Assistance",
)
def get_code_debug(
    request: DebugRequest, ai_client: AIClient = Depends(get_ai_client)
) -> DebugResponse:
    try:
        result = ai_client.get_debug(code=request.code, level=request.level)
        return DebugResponse(fixed_code=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI provider error: {e}",
        )

# ==============================================================================
# Modular Routers
# ==============================================================================
app.include_router(comment.router, prefix=settings.API_V1_STR)
app.include_router(run.router, prefix=settings.API_V1_STR)
app.include_router(debug.router, prefix=settings.API_V1_STR)
app.include_router(docs.router, prefix=settings.API_V1_STR)
app.include_router(voice.router, prefix="/api/v1", tags=["voice"])