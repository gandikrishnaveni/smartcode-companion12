# # File: smart_code_companion/routers/debug.py

# import io
# import sys
# import traceback
# from fastapi import APIRouter, HTTPException, Depends, status
# from smart_code_companion.core.models import DebugRequest, DebugResponse
# from smart_code_companion.ai_clients.base import AIClient
# from smart_code_companion.ai_clients.client import get_ai_client

# router = APIRouter()


# @router.post("/debug", response_model=DebugResponse, tags=["Debugging"])
# def debug_code_ai(request: DebugRequest, ai_client: AIClient = Depends(get_ai_client)):
#     """
#     Run the user code safely and return:
#       - fixed_code: original or AI-suggested
#       - error: first exception (if any)
#       - explanation: human-readable explanation
#       - suggestion: optional fix from AI
#     """
#     code = request.code
#     level = request.level.lower() if request.level else "beginner"

#     old_stdout = sys.stdout
#     sys.stdout = mystdout = io.StringIO()

#     try:
#         # Try running the entire code at once
#         exec(code, {})
#         # No error: return original code
#         return DebugResponse(
#             fixed_code=code,
#             error=None,
#             explanation=None,
#             suggestion=None
#         )
#     except Exception as e:
#         # Capture first error
#         error_msg = str(e)
#         tb = traceback.format_exc()

#         # Get AI suggestion if available
#         try:
#             ai_output = ai_client.get_debug(code, level)
#             suggestion = ai_output.strip() if ai_output else None
#         except Exception:
#             suggestion = None

#         explanation = f"The error \"{error_msg}\" occurred. Please check your code."

#         return DebugResponse(
#             fixed_code=code,
#             error=error_msg,
#             explanation=explanation,
#             suggestion=suggestion
#         )
#     finally:
#         sys.stdout = old_stdout
# smart_code_companion/routers/debug.py
# File: smart_code_companion/routers/debug.py

import ast
import traceback
from fastapi import APIRouter, Depends
from smart_code_companion.core.models import DebugRequest, DebugResponse
from smart_code_companion.ai_clients.base import AIClient
from smart_code_companion.ai_clients import get_ai_client
import sys
import io
import re

router = APIRouter()

# ---------------- Helper to parse AI output ----------------
def parse_ai_debug(ai_output: str):
    """
    Parses AI output into structured fields for DebugResponse.
    Returns error, explanation, suggestion, and fixed_code.
    """
    # Extract code blocks
    code_blocks = re.findall(r"Code:\s*(.*?)(?=(?:\nError:|\Z))", ai_output, flags=re.DOTALL)
    fixed_code = "\n\n".join([c.strip() for c in code_blocks]) if code_blocks else None

    # Extract first Error/Explanation/Suggestion
    error_match = re.search(r"Error:\s*(.*)", ai_output)
    explanation_match = re.search(r"Explanation:\s*(.*)", ai_output)
    suggestion_match = re.search(r"(?:Suggestion|Fix):\s*(.*)", ai_output)

    error = error_match.group(1).strip() if error_match else None
    explanation = explanation_match.group(1).strip() if explanation_match else None
    suggestion = suggestion_match.group(1).strip() if suggestion_match else None

    return error, explanation, suggestion, fixed_code

# ---------------- Debug Route ----------------
@router.post("/debug", response_model=DebugResponse, tags=["Debugging"])
def debug_code_ai(request: DebugRequest, ai_client: AIClient = Depends(get_ai_client)):
    """
    Executes user code safely and, on error, calls AI client to get:
      - error
      - explanation
      - suggestion
      - fixed_code
    Respects the requested skill level (beginner/intermediate/advanced).
    """
    code = request.code

    # Capture stdout to prevent unwanted prints
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()

    try:
        # Try executing the code safely
        exec(code, {})
        # No exception -> return code as-is
        return DebugResponse(
            fixed_code=code,
            error=None,
            explanation=None,
            suggestion=None
        )
    except Exception:
        # If error occurs, ask AI to debug
        try:
            ai_output = ai_client.get_debug(code, request.level)
            error, explanation, suggestion, fixed_code = parse_ai_debug(ai_output)
            return DebugResponse(
                fixed_code=fixed_code or code,
                error=error or "Error occurred",
                explanation=explanation or "No detailed explanation provided.",
                suggestion=suggestion or "Check your code and fix the error."
            )
        except Exception as e:
            # Fallback in case AI call fails
            return DebugResponse(
                fixed_code=code,
                error=str(e),
                explanation="AI debugging failed. Please check your code manually.",
                suggestion=None
            )
    finally:
        sys.stdout = old_stdout
