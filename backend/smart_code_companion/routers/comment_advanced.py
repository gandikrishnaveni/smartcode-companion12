from fastapi import APIRouter, Depends, HTTPException
from smart_code_companion.core.models import CodeRequest, CommentResponse, FunctionComment, SpeechCommentRequest
from smart_code_companion.ai_clients.base import AIClient
from smart_code_companion.ai_clients import get_ai_client
import ast

router = APIRouter()

@router.post("/comment", response_model=CommentResponse, tags=["AI"])
def function_wise_comment(request: CodeRequest, ai_client: AIClient = Depends(get_ai_client)):
    """
    Function-wise commenting: parses code functions and generates comments for each.
    """
    try:
        tree = ast.parse(request.code)
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                fn_code = ast.get_source_segment(request.code, node)
                comment_text = ai_client.get_comment(fn_code, request.level)
                functions.append(FunctionComment(name=node.name, comment=comment_text, level=request.level))
        overall_comment = ai_client.get_comment(request.code, request.level)
        return CommentResponse(comment=overall_comment, functions=functions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/speech_comment", response_model=CommentResponse, tags=["AI"])
def speech_comment(request: SpeechCommentRequest, ai_client: AIClient = Depends(get_ai_client)):
    """
    Converts speech (base64 audio) to text comment.
    """
    try:
        transcript = ai_client.transcribe_audio(request.audio_base64)
        return CommentResponse(comment=transcript, voice_comment=transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
