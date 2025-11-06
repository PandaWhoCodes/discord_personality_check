"""Slash command registration and handlers."""

import logging

import discord
from discord import app_commands

logger = logging.getLogger(__name__)


def register_slash_commands(tree: app_commands.CommandTree, context: dict) -> None:
    """
    Register all slash commands with the command tree.

    Args:
        tree: Discord command tree to register commands with
        context: Shared context containing bot resources (questions, sessions, etc.)
    """

    @tree.command(name="personality", description="Take the full MBTI personality test")
    async def personality_full(interaction: discord.Interaction) -> None:
        """Slash command to start the full personality test in DM."""
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        username = f"{interaction.user.name}#{interaction.user.discriminator}"

        try:
            # Send DM to user
            dm_channel = await interaction.user.create_dm()

            await context["start_test_func"](
                dm_channel, user_id, username, is_dummy=False, **context["test_data"]
            )

            await interaction.followup.send(
                "✅ Check your DMs! I've started the personality test there.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I couldn't send you a DM. Please enable DMs from server members in your privacy settings.",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"Error starting test for {username}: {e}")
            await interaction.followup.send(
                "❌ An error occurred while starting the test. Please try again.", ephemeral=True
            )

    @tree.command(name="personality-quick", description="Take a quick 5-question personality test")
    async def personality_quick(interaction: discord.Interaction) -> None:
        """Slash command to start the quick personality test in DM."""
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        username = f"{interaction.user.name}#{interaction.user.discriminator}"

        try:
            # Send DM to user
            dm_channel = await interaction.user.create_dm()

            await context["start_test_func"](
                dm_channel, user_id, username, is_dummy=True, **context["test_data"]
            )

            await interaction.followup.send(
                "✅ Check your DMs! I've started the quick test there.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I couldn't send you a DM. Please enable DMs from server members in your privacy settings.",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"Error starting test for {username}: {e}")
            await interaction.followup.send(
                "❌ An error occurred while starting the test. Please try again.", ephemeral=True
            )

    logger.info("Slash commands registered: /personality, /personality-quick")
