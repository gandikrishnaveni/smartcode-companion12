# File: smart_code_companion/routers/comment.py
# Description: Provides real-time AI comments for code lines or functions

import ast
from fastapi import APIRouter, Depends, HTTPException, status
from smart_code_companion.core.models import CodeRequest, CommentResponse, FunctionComment, HealthResponse
from smart_code_companion.ai_clients.base import AIClient
from smart_code_companion.ai_clients import get_ai_client
from smart_code_companion.ai_clients.watson_sst import WatsonSTTClient
router = APIRouter()


# ---------------- Health Endpoint -----------------
@router.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health_check():
    return HealthResponse(status="ok")


# ---------------- Helper Function -----------------
def annotate_code(code: str, ai_client: AIClient, level: str):
    print("DEBUG: Original code received:\n", code)  # <-- ADD THIS LINE

    try:
        tree = ast.parse(code)
    except SyntaxError:
        comment_text = ai_client.get_comment(code, level)
        result = f"{code}  # {comment_text}"
        print("DEBUG: Annotated code returned:\n", result)  # <-- ADD THIS
        return result, []

    lines = code.splitlines()
    annotated_lines = lines.copy()
    function_comments = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno - 1
            end = getattr(node, "end_lineno", node.lineno)
            func_code = "\n".join(lines[start:end])
            comment_text = ai_client.get_comment(func_code, level)
            function_comments.append(FunctionComment(name=node.name, comment=comment_text, level=level))
            annotated_lines[end-1] = f"{lines[end-1]}  # {comment_text}"

        elif isinstance(node, (ast.Assign, ast.Expr)):
            line_no = node.lineno - 1
            stmt_code = lines[line_no].strip()
            if stmt_code:
                stmt_comment = ai_client.get_comment(stmt_code, level)
                annotated_lines[line_no] = f"{lines[line_no]}  # {stmt_comment}"

    result = "\n".join(annotated_lines)
    print("DEBUG: Annotated code returned:\n", result)  # <-- ADD THIS
    return result, function_comments


# ---------------- Comment Endpoint -----------------
@router.post("/comment", response_model=CommentResponse, tags=["AI"])
def get_code_comment(
    request: CodeRequest,
    ai_client: AIClient = Depends(get_ai_client)
):
    """
    Receives code (single line or block), returns:
      - Inline comments for each statement
      - Function-level comments
      - Optional voice comment
    """
    try:
        annotated_code, functions = annotate_code(request.code, ai_client, request.level)
        return CommentResponse(comment=annotated_code, functions=functions, voice_comment="")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating comments: {e}"
        )


# ---------------- Single-line real-time comment -----------------
@router.post("/comment-line", response_model=CommentResponse, tags=["AI"])
def comment_line(
    request: CodeRequest,
    ai_client: AIClient = Depends(get_ai_client)
):
    """
    Generates a comment for a single line of code (useful for 'press Enter' feature).
    """
    try:
        comment_text = ai_client.get_comment(request.code, request.level)
        annotated_line = f"{request.code}  # {comment_text}"
        return CommentResponse(comment=annotated_line, functions=[], voice_comment="")
    except Exception as e:
        return CommentResponse(comment=f"{request.code}  # Error: {e}", functions=[], voice_comment="")
from pydantic import BaseModel

class VoiceCommentRequest(BaseModel):
    audio_base64: str
    code: str
    level: str = "beginner"

@router.post("/voice-comment", response_model=CommentResponse, tags=["AI"])
def voice_comment(request: VoiceCommentRequest, ai_client: AIClient = Depends(get_ai_client)):
    """
    Receives audio + code, converts speech to text, and returns annotated code.
    """
    try:
        # Watson STT
        stt_client = WatsonSTTClient()
        spoken_text = stt_client.transcribe(request.audio_base64)

        # Combine spoken instructions with existing code
        combined_code = f"# Voice instructions:\n# {spoken_text}\n{request.code}"

        # Annotate the code using your normal AI client
        annotated_code, functions = annotate_code(combined_code, ai_client, request.level)

        return CommentResponse(comment=annotated_code, functions=functions, voice_comment=spoken_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice comment failed: {e}")