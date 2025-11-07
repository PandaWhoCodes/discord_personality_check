# FiT Discord Bot (Faith in Tech)

A modular Discord bot providing engagement tools for Christian communities. Currently features a comprehensive MBTI personality test with Biblical character alignments, spiritual gifts, and ministry suggestions.

## About FiT (Faith in Tech)

This bot serves as a platform for multiple engagement tools designed to foster community, spiritual growth, and interaction in Discord servers. The modular architecture allows easy addition of new commands and features.

## Current Features

### MBTI Personality Test
- 44-question comprehensive personality assessment
- Interactive button-based interface
- Personalized results with:
  - Biblical character matches
  - Spiritual gifts alignment
  - Ministry suggestions
  - Detailed personality descriptions
- Session persistence (resume incomplete tests)
- Message analytics tracking

### Technical Features
- Modular command system (easily extensible)
- Text commands and slash commands support
- Clean Architecture design
- Turso (libSQL) database with sync
- Pre-commit hooks with Black formatting
- Comprehensive test suite

## Setup

### Prerequisites

- Python 3.10+
- Discord Bot Token (see Discord Developer Portal)
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/PandaWhoCodes/FiT_discord_bot.git
cd FiT_discord_bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - The `.env` file is already created with your bot credentials
   - Verify the settings are correct

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Your bot application (ID: 1435683561004077161) should already be created
3. Ensure the bot has these permissions:
   - Send Messages
   - Use Slash Commands
   - Read Message History
4. Bot Scopes needed:
   - `bot`
   - `applications.commands`
5. Invite the bot to your server using the OAuth2 URL generator

### Running the Bot

First, test that everything is set up correctly:
```bash
source venv/bin/activate  # Activate virtual environment
python test_setup.py      # Run setup tests
```

Then start the bot:
```bash
./run.sh                  # Quick start script
```

Or manually:
```bash
source venv/bin/activate
python -m src.main
```

The bot will:
- Connect to Discord
- Initialize the database
- Load questions and personality profiles
- Register the `/get-personality` slash command

## Usage

### Available Commands

#### Personality Test
- **Text commands**:
  - `start test` - Begin the full 44-question MBTI test
  - `start dummy test` - Quick test with fewer questions
- **Slash commands**:
  - `/personality` - Full MBTI personality test
  - `/personality-quick` - Abbreviated test version

### Taking the Personality Test

1. In any Discord channel where the bot has access, use one of the commands above

2. The bot will send you a DM (or ephemeral message) with the first question

3. Click the appropriate button to answer each question

4. Progress through all questions

5. Receive your MBTI type with Biblical character alignments and ministry suggestions

### Results Include

- Your 4-letter MBTI type (e.g., INTJ, ENFP)
- Biblical characters who share your personality
- Spiritual gifts associated with your type
- Ministry suggestions aligned with your strengths
- Dimension scores showing your preferences

## Project Structure

```
FiT_discord_bot/
├── src/
│   ├── main.py              # Bot initialization & event loop
│   ├── commands/            # Command modules
│   │   ├── text_commands.py    # Decorator-based text commands
│   │   └── slash_commands.py   # Slash command registration
│   ├── analytics/           # Message tracking
│   │   └── messages.py
│   ├── database.py          # Turso database operations
│   ├── models.py            # Data models (UserSession, etc.)
│   └── personality.py       # Test logic & button UI
├── data/
│   ├── questions.yaml       # MBTI test questions
│   └── personality_profiles.yaml  # Biblical profiles
├── docs/
│   └── plans/               # Design documentation
├── CLAUDE.md                # Technical documentation
├── .env                     # Environment configuration
├── requirements.txt         # Python dependencies
├── run.sh                   # Quick start script
└── setup.sh                 # Full environment setup
```

## Architecture

The bot uses a **modular command system** for easy extensibility:

### Key Design Patterns

1. **Text Commands (Decorator Pattern)**: Add new text commands by decorating functions in `text_commands.py`
2. **Slash Commands (Registration Function)**: Register slash commands in `slash_commands.py`
3. **Command Context**: Shared resources passed to all commands

### Adding New Commands

To add a text command:
```python
@text_command("hello")
async def handle_hello(message, context):
    await message.channel.send("Hi there!")
```

To add a slash command:
```python
@tree.command(name="hello", description="Say hello")
async def hello(interaction):
    await interaction.response.send_message("Hi!")
```

**main.py never needs to change!** This makes adding new engagement tools simple and maintainable.

## Database

The bot uses **Turso (libSQL)** for cloud-synced database storage. Tables:

- `test_results`: Completed personality test results
- `messages`: Analytics data for all Discord messages

### Database Sync Strategy
- **Startup**: Pulls latest from Turso
- **After writes**: Commits and syncs to Turso
- No periodic background syncs (keeps architecture simple)

Configuration in `.env`:
```bash
TURSO_DATABASE_URL=libsql://...
TURSO_AUTH_TOKEN=...
```

## Troubleshooting

### Bot doesn't come online
- Check that your bot token in `.env` is correct
- Verify the bot has proper permissions in Discord
- Check `bot.log` for error messages

### Slash command doesn't appear
- Wait a few minutes for Discord to sync commands
- Try kicking and re-inviting the bot
- Check bot has `applications.commands` scope

### Database errors
- Verify `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` in `.env`
- Check network connectivity to Turso
- Review database sync logs

### SSL Certificate errors (macOS)
If you see `SSL: CERTIFICATE_VERIFY_FAILED` errors:
- The bot now includes certifi which should fix this automatically
- If issues persist, run: `pip install --upgrade certifi`
- Alternatively, install certificates system-wide:
  ```bash
  /Applications/Python\ 3.11/Install\ Certificates.command
  ```

## Development

### Running Tests

```bash
python test_setup.py          # Import and setup tests
python test_modular_setup.py  # Command registration tests
```

### Code Quality

The project uses pre-commit hooks for automatic code formatting:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Format code
black src/ --line-length=100
```

## Roadmap

Future engagement tools planned:
- Daily devotional commands
- Prayer request management
- Scripture memory games
- Community polls and surveys
- Event management features

## Contributing

This is a Faith in Tech community project. Contributions are welcome! Please ensure:
- Code follows Black formatting (100 char line length)
- Pre-commit hooks pass
- New commands use the modular command system
- Documentation is updated

## License

This project is for ministry and community use.

## Credits

Built with:
- discord.py 2.3.0+
- Turso (libSQL) database
- Black formatter
- Pre-commit hooks
- PyYAML
