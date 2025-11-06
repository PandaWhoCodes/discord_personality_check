"""Personality test logic, scoring, and Discord UI components."""

import logging
from typing import Any

import discord
from discord.ui import Button, View
import yaml

from .models import Question, PersonalityProfile, UserSession, Scores
from .database import save_test_result

logger = logging.getLogger(__name__)

# Constants
DIMENSIONS = ["EI", "SN", "TF", "JP"]
DIMENSION_PAIRS = [("E", "I"), ("S", "N"), ("T", "F"), ("J", "P")]


def load_questions() -> list[Question]:
    """Load questions from YAML file."""
    with open("data/questions.yaml", "r") as f:
        data = yaml.safe_load(f)
        return [Question.from_dict(q) for q in data["questions"]]


def load_profiles() -> dict[str, PersonalityProfile]:
    """Load personality profiles from YAML file."""
    with open("data/personality_profiles.yaml", "r") as f:
        data = yaml.safe_load(f)
        return {
            personality_type: PersonalityProfile.from_dict(profile)
            for personality_type, profile in data.items()
        }


def get_dummy_questions(all_questions: list[Question]) -> list[Question]:
    """Get 5 sample questions for quick test - one from each dimension group."""
    dummy = []
    # Get first question from each dimension
    for dimension in DIMENSIONS:
        for q in all_questions:
            if q.dimension == dimension and q not in dummy:
                dummy.append(q)
                break
    # Add one more from EI
    for q in all_questions:
        if q.dimension == "EI" and q not in dummy:
            dummy.append(q)
            break
    return dummy[:5]


def calculate_personality(scores: Scores) -> str:
    """Calculate MBTI personality type from scores."""
    personality = ""
    for pos, neg in DIMENSION_PAIRS:
        personality += pos if scores.get(pos, 0) > scores.get(neg, 0) else neg
    return personality


def format_result_message(personality_type: str, profile: PersonalityProfile) -> str:
    """Format the result message with profile info."""
    msg = "**Test Complete!**\n\n"
    msg += f"**Your Personality Type: {personality_type}**\n\n"
    msg += f"{profile.description}\n\n"

    msg += "**Biblical Characters:**\n"
    for char in profile.biblical_characters[:2]:  # Show first 2
        msg += f"• {char}\n"

    msg += "\n**Your Spiritual Gifts:**\n"
    for gift in profile.spiritual_gifts[:3]:  # Show first 3
        msg += f"• {gift}\n"

    msg += "\n**Ministry Suggestions:**\n"
    for suggestion in profile.ministry_suggestions[:2]:  # Show first 2
        msg += f"• {suggestion}\n"

    msg += "\n✅ Your results have been saved!\n"
    msg += "\nType 'start test' for full test or 'start dummy test' for quick test!"

    return msg


class QuestionView(View):
    """View with buttons for answering questions."""

    def __init__(
        self,
        question: Question,
        session: UserSession,
        questions: list[Question],
        profiles: dict[str, PersonalityProfile],
        user_id: int,
        username: str,
        user_sessions: dict[int, UserSession],
    ):
        super().__init__(timeout=300)  # 5 minute timeout
        self.question = question
        self.session = session
        self.questions = questions
        self.profiles = profiles
        self.user_id = user_id
        self.username = username
        self.user_sessions = user_sessions

        # Add buttons for each option
        for i, option in enumerate(question.options):
            button = Button(
                label=f"{chr(65+i)}",
                style=discord.ButtonStyle.primary,
                custom_id=f"answer_{chr(65+i)}",
            )
            button.callback = self._create_callback(i)
            self.add_item(button)

    def _create_callback(self, answer_idx: int):
        """Create callback for button."""

        async def callback(interaction: discord.Interaction) -> None:
            # Make sure the person clicking is the one who started the test
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This is not your test!", ephemeral=True)
                return

            await self._handle_answer(interaction, answer_idx)

        return callback

    async def _handle_answer(self, interaction: discord.Interaction, answer_idx: int) -> None:
        """Handle user's answer to current question."""
        option = self.question.options[answer_idx]
        weight = option.weight

        # Record answer
        self.session.answers.append(chr(65 + answer_idx))

        # Update scores based on dimension and weight
        self._update_scores(weight)

        # Move to next question
        self.session.current_question += 1

        # Disable all buttons
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

        # Check if test is complete
        if self.session.current_question >= len(self.questions):
            await self._complete_test(interaction)
        else:
            await self._ask_next_question(interaction)

    def _update_scores(self, weight: int) -> None:
        """Update session scores based on question dimension and weight."""
        dimension = self.question.dimension

        if weight > 0:
            # Positive weight goes to first letter (E, S, T, J)
            self.session.scores[dimension[0]] += abs(weight)
        else:
            # Negative weight goes to second letter (I, N, F, P)
            self.session.scores[dimension[1]] += abs(weight)

    async def _complete_test(self, interaction: discord.Interaction) -> None:
        """Calculate results and save to database."""
        personality = calculate_personality(self.session.scores)
        profile = self.profiles[personality]

        # Save to database
        test_type = "dummy" if self.session.is_dummy else "full"
        save_test_result(
            self.user_id, self.username, personality, test_type, self.session.scores, profile
        )

        result_msg = format_result_message(personality, profile)
        await interaction.followup.send(result_msg)

        # Clean up session
        if self.user_id in self.user_sessions:
            del self.user_sessions[self.user_id]

        logger.info(f"Test completed for {self.username}: {personality}")

    async def _ask_next_question(self, interaction: discord.Interaction) -> None:
        """Send the next question to the user."""
        next_q = self.questions[self.session.current_question]
        options_text = "\n".join(
            [f"{chr(65+i)}) {opt.text}" for i, opt in enumerate(next_q.options)]
        )

        view = QuestionView(
            next_q,
            self.session,
            self.questions,
            self.profiles,
            self.user_id,
            self.username,
            self.user_sessions,
        )

        await interaction.followup.send(
            f"Question {self.session.current_question + 1}/{len(self.questions)}: "
            f"{next_q.text}\n\n{options_text}",
            view=view,
        )
