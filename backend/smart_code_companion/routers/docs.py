# smart_code_companion/routers/docs.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DocsResponse(BaseModel):
    title: str
    content: str

@router.get("/docs_content", response_model=DocsResponse, tags=["Docs"])
def get_docs():
    """
    Returns embedded documentation / coding tips.
    """
    return DocsResponse(
        title="Smart Code Companion Documentation",
        content="""
        Welcome to Smart Code Companion!

        Features:
        1. /comment - AI-powered code feedback
        2. /run - Execute Python code
        3. /debug - Debug code line by line
        4. /docs_content - This documentation

        Usage:
        - POST /api/v1/comment with your code to get suggestions
        - POST /api/v1/run to execute code safely
        - POST /api/v1/debug to inspect errors and outputs
        """
    )
