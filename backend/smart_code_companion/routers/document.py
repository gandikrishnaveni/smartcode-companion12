from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from smart_code_companion.ai_clients import get_ai_client

router = APIRouter()

class DocumentRequest(BaseModel):
    code: str
    level: str = "beginner"  # optional: adjust verbosity

class DocumentResponse(BaseModel):
    documentation: str

@router.post("/document", response_model=DocumentResponse)
async def generate_documentation(req: DocumentRequest):
    try:
        ai_client = get_ai_client()
        # Ask AI client to generate documentation
        documentation = ai_client.get_documentation(req.code, req.level)
        return {"documentation": documentation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Documentation error: {e}")
