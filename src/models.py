"""Data models for the personality test bot."""

from dataclasses import dataclass, field
from typing import TypeAlias

# Type aliases for clarity
Scores: TypeAlias = dict[str, int]
OptionsList: TypeAlias = list[dict[str, str | int]]


@dataclass
class QuestionOption:
    """A single answer option for a question."""

    text: str
    weight: int


@dataclass
class Question:
    """A personality test question."""

    text: str
    dimension: str  # EI, SN, TF, or JP
    options: list[QuestionOption]

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        """Create Question from dictionary loaded from YAML."""
        options = [
            QuestionOption(text=opt["text"], weight=opt["weight"]) for opt in data["options"]
        ]
        return cls(text=data["text"], dimension=data["dimension"], options=options)


@dataclass
class PersonalityProfile:
    """MBTI personality profile with biblical context."""

    description: str
    biblical_characters: list[str]
    spiritual_gifts: list[str]
    ministry_suggestions: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> "PersonalityProfile":
        """Create PersonalityProfile from dictionary loaded from YAML."""
        return cls(
            description=data["description"],
            biblical_characters=data["biblical_characters"],
            spiritual_gifts=data["spiritual_gifts"],
            ministry_suggestions=data["ministry_suggestions"],
        )


@dataclass
class UserSession:
    """Tracks a user's test progress."""

    current_question: int = 0
    answers: list[str] = field(default_factory=list)
    scores: Scores = field(
        default_factory=lambda: {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    )
    is_dummy: bool = False
    questions: list[Question] = field(default_factory=list)
