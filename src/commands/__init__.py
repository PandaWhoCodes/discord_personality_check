"""Command handlers for the Discord bot."""

from .text_commands import text_command, handle_text_command
from .slash_commands import register_slash_commands

__all__ = ["text_command", "handle_text_command", "register_slash_commands"]
