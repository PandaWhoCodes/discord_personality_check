"""Text command system using decorator-based registration."""

import logging
from typing import Callable, Dict

import discord

logger = logging.getLogger(__name__)

# Global registry for text commands
_text_commands: Dict[str, Callable] = {}


def text_command(trigger: str):
    """
    Decorator to register a text command handler.

    Example:
        @text_command("start test")
        async def handle_start_test(message, context):
            # handler code
    """

    def decorator(func: Callable):
        _text_commands[trigger.lower()] = func
        logger.info(f"Registered text command: '{trigger}'")
        return func

    return decorator


async def handle_text_command(message: discord.Message, context: dict) -> bool:
    """
    Check if message matches any registered text command and execute it.

    Args:
        message: The Discord message object
        context: Shared context containing bot resources (questions, sessions, etc.)

    Returns:
        True if a command was handled, False otherwise
    """
    content = message.content.lower().strip()

    if content in _text_commands:
        handler = _text_commands[content]
        logger.info(f"Executing text command '{content}' from {message.author.name}")
        try:
            await handler(message, context)
            return True
        except Exception as e:
            logger.error(f"Error executing command '{content}': {e}", exc_info=True)
            await message.channel.send(
                "❌ An error occurred while processing your command. Please try again."
            )
            return False

    return False


# ============================================================================
# Command Handlers
# ============================================================================


@text_command("start test")
async def handle_start_test(message: discord.Message, context: dict) -> None:
    """Start the full MBTI personality test."""
    user_id = message.author.id
    username = f"{message.author.name}#{message.author.discriminator}"

    await context["start_test_func"](
        message.channel, user_id, username, is_dummy=False, **context["test_data"]
    )


@text_command("start dummy test")
async def handle_dummy_test(message: discord.Message, context: dict) -> None:
    """Start the quick 5-question personality test."""
    user_id = message.author.id
    username = f"{message.author.name}#{message.author.discriminator}"

    await context["start_test_func"](
        message.channel, user_id, username, is_dummy=True, **context["test_data"]
    )
