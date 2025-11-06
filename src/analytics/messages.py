"""Message analytics - store and track all messages for insights."""

import logging
from datetime import datetime, timezone

import discord

from ..database import save_message

logger = logging.getLogger(__name__)


async def store_message(message: discord.Message) -> None:
    """
    Extract message metadata and store in database for analytics.

    Args:
        message: The Discord message object to store

    Stores:
        - User information (ID, username)
        - Message content and metadata
        - Channel/server information
        - Message characteristics (attachments, embeds, mentions)
        - Timestamps
    """
    try:
        # Determine if message is a DM
        is_dm = isinstance(message.channel, discord.DMChannel)

        # Extract channel information
        channel_id = str(message.channel.id)
        channel_name = message.channel.name if hasattr(message.channel, "name") else "DM"

        # Extract server information (None for DMs)
        server_id = str(message.guild.id) if message.guild else None
        server_name = message.guild.name if message.guild else None

        # Extract reply information
        reply_to_message_id = None
        if message.reference and message.reference.message_id:
            reply_to_message_id = str(message.reference.message_id)

        # Build message data dictionary
        message_data = {
            "message_id": str(message.id),
            "discord_user_id": str(message.author.id),
            "discord_username": f"{message.author.name}#{message.author.discriminator}",
            "message_text": message.content,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "server_id": server_id,
            "server_name": server_name,
            "is_dm": is_dm,
            "message_length": len(message.content),
            "has_attachments": len(message.attachments) > 0,
            "has_embeds": len(message.embeds) > 0,
            "has_mentions": len(message.mentions) > 0,
            "reply_to_message_id": reply_to_message_id,
            "created_at": message.created_at.isoformat(),
            "edited_at": message.edited_at.isoformat() if message.edited_at else None,
        }

        # Save to database
        save_message(message_data)

        logger.debug(
            f"Stored message {message.id} from {message.author.name} "
            f"in {'DM' if is_dm else channel_name}"
        )

    except Exception as e:
        # Don't let analytics failures break the bot
        logger.error(f"Failed to store message {message.id}: {e}", exc_info=True)
