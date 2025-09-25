from smart_code_companion.ai_clients.base import AIClient

class MockAIClient(AIClient):
    """
    A mock AI client for testing and development.
    Returns predefined responses without real API calls.
    """

    def get_comment(self, code: str, level: str) -> str:  # level as string
        responses = {
            "beginner": (
                "// MOCK RESPONSE (Beginner):\n"
                "// Good start! Add comments and descriptive variable names."
            ),
            "intermediate": (
                "// MOCK RESPONSE (Intermediate):\n"
                "// Solid logic. Consider smaller functions and error handling."
            ),
            "advanced": (
                "// MOCK RESPONSE (Advanced):\n"
                "// Algorithm is correct. Optimize data structures for performance."
            ),
        }
        return responses.get(level.lower(), "// MOCK RESPONSE: Unknown skill level.")
