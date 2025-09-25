from abc import ABC, abstractmethod
from smart_code_companion.core.models import SkillLevel

class AIClient(ABC):
    """
    Abstract Base Class (Interface) for all AI clients.

    This defines the contract that every AI client implementation must follow.
    It ensures they all have a `get_comment` method with the same signature,
    allowing the main application to treat them interchangeably.
    """

    @abstractmethod
    def get_comment(self, code: str, level: SkillLevel) -> str:
        """
        Generates a comment for the given code based on the user's skill level.

        Args:
            code: The source code to review.
            level: The user's skill level.

        Returns:
            A string containing the AI-generated feedback.
        """
        pass
