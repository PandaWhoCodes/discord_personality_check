"""Discord bot with personality test using buttons and Turso database."""

import logging
import os
import ssl
import sys

import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv

from .analytics import store_message
from .commands import handle_text_command, register_slash_commands
from .database import init_database, close_database
from .models import UserSession
from .personality import load_questions, load_profiles, get_dummy_questions, QuestionView

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Store user sessions: {user_id: UserSession}
user_sessions: dict[int, UserSession] = {}


def create_ssl_connector() -> aiohttp.TCPConnector | None:
    """Create SSL connector for Discord client (macOS compatibility)."""
    try:
        import certifi

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        logger.info("Using certifi SSL certificates")
        return connector
    except ImportError:
        logger.warning("certifi not available, using system SSL certificates")
        return None


async def start_test(
    channel: discord.abc.Messageable,
    user_id: int,
    username: str,
    is_dummy: bool,
    all_questions,
    dummy_questions,
    profiles,
    sessions: dict[int, UserSession],
) -> None:
    """Start a personality test for a user."""
    logger.info(f"⚡ start_test() called for {username} (user_id: {user_id}, is_dummy: {is_dummy})")

    # Check if user already has an active session
    if user_id in sessions:
        logger.warning(f"User {username} already has an active session!")
        await channel.send("⚠️ You already have an active test! Please complete it first.")
        return

    questions = dummy_questions if is_dummy else all_questions
    test_name = "Quick Dummy Test" if is_dummy else "Full Personality Test"

    logger.info(f"Starting {'DUMMY' if is_dummy else 'FULL'} test for {username}")

    # Initialize session
    session = UserSession(is_dummy=is_dummy, questions=questions)
    sessions[user_id] = session

    # Get first question
    question = questions[0]
    options_text = "\n".join([f"{chr(65+i)}) {opt.text}" for i, opt in enumerate(question.options)])

    view = QuestionView(question, session, questions, profiles, user_id, username, sessions)

    header = f"**{test_name} Started!**"
    if is_dummy:
        header += " (5 questions)"

    logger.info(f"📤 Sending initial question to channel...")
    message = await channel.send(
        f"{header}\n\n" f"Question 1/{len(questions)}: {question.text}\n\n" f"{options_text}",
        view=view,
    )
    logger.info(f"✅ Message sent successfully (ID: {message.id})")


async def async_main() -> None:
    """Async main entry point."""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        logger.error("DISCORD_BOT_TOKEN environment variable is required")
        sys.exit(1)

    # Initialize database
    init_database()

    # Load questions and profiles
    try:
        all_questions = load_questions()
        profiles = load_profiles()
        dummy_questions = get_dummy_questions(all_questions)
        logger.info(f"Loaded {len(all_questions)} questions and {len(profiles)} profiles")
        logger.info(f"Dummy test has {len(dummy_questions)} questions")
    except Exception as e:
        logger.error(f"Failed to load questions or profiles: {e}")
        sys.exit(1)

    # Create SSL connector
    connector = create_ssl_connector()

    # Setup intents
    intents = discord.Intents.default()
    intents.message_content = True

    # Create bot
    bot = discord.Client(intents=intents, connector=connector)
    tree = app_commands.CommandTree(bot)

    # Build context for commands
    command_context = {
        "start_test_func": start_test,
        "test_data": {
            "all_questions": all_questions,
            "dummy_questions": dummy_questions,
            "profiles": profiles,
            "sessions": user_sessions,
        },
    }

    # Register slash commands
    register_slash_commands(tree, command_context)

    @bot.event
    async def on_ready() -> None:
        """Called when the bot is ready."""
        await tree.sync()
        logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
        logger.info("Bot is ready!")
        logger.warning(
            "⚠️ If you see this message multiple times, you have multiple bot instances running!"
        )

    @bot.event
    async def on_message(message: discord.Message) -> None:
        """Handle all incoming messages - store for analytics and process commands."""
        # Ignore messages from the bot itself
        if message.author == bot.user:
            return

        # Ignore messages from other bots
        if message.author.bot:
            return

        # Store message for analytics
        await store_message(message)

        # Handle text commands
        await handle_text_command(message, command_context)

    logger.info("Starting Discord bot with button support and database storage...")
    await bot.start(bot_token)


def main() -> None:
    """Main entry point."""
    import asyncio

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        close_database()


if __name__ == "__main__":
    main()
