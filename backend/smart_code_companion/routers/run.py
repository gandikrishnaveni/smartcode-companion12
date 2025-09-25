# File: smart_code_companion/routers/run.py
# Description: API route for safely executing Python code.

import subprocess
import sys
from fastapi import APIRouter, HTTPException, status
from smart_code_companion.models.pydantic_models import RunRequest, RunResponse

router = APIRouter()

@router.post(
    "/run",
    response_model=RunResponse,
    tags=["Execution"],
)
def execute_code(request: RunRequest):
    """
    Executes Python code in a sandboxed subprocess for safety.
    Captures and returns stdout, stderr, and the exit code.
    """
    try:
        # Execute the code using the same Python interpreter that runs the app.
        # A timeout is crucial to prevent long-running or infinite-loop code.
        process = subprocess.run(
            [sys.executable, "-c", request.code],
            capture_output=True,
            text=True,
            timeout=5,  # 5-second timeout for safety
        )
        return RunResponse(
            stdout=process.stdout,
            stderr=process.stderr,
            exit_code=process.returncode,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Code execution timed out after 5 seconds.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during execution: {e}",
        )
