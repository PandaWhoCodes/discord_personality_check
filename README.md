# Discord MBTI Personality Bot

A Discord bot that administers a comprehensive 44-question MBTI personality test with Biblical character alignments, spiritual gifts, and ministry suggestions.

## Features

- 44-question MBTI test covering all 4 personality dimensions
- Interactive button-based interface
- Personalized results with:
  - Biblical character matches
  - Spiritual gifts alignment
  - Ministry suggestions
  - Detailed personality descriptions
- Session persistence (resume incomplete tests)
- Clean Architecture design
- SQLite database storage

## Setup

### Prerequisites

- Python 3.10+
- Discord Bot Token (see Discord Developer Portal)
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd discord_personality_check
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

### Taking the Test

1. In any Discord channel where the bot has access, type:
   ```
   /get-personality
   ```

2. The bot will send you an ephemeral message (only you can see it) with the first question

3. Click the appropriate button (A, B, C, or D) to answer each question

4. Progress through all 44 questions

5. Receive your MBTI type with Biblical insights

### Results Include

- Your 4-letter MBTI type (e.g., INTJ, ENFP)
- Biblical characters who share your personality
- Spiritual gifts associated with your type
- Ministry suggestions aligned with your strengths
- Dimension scores showing your preferences

## Project Structure

```
discord_personality_check/
├── src/
│   ├── domain/              # Core business logic
│   │   ├── models/         # Data models
│   │   ├── services/       # Business services
│   │   └── interfaces/     # Repository contracts
│   ├── application/         # Use cases
│   │   ├── commands/       # Command handlers
│   │   └── queries/        # Query handlers
│   ├── infrastructure/      # External concerns
│   │   ├── discord/        # Discord bot integration
│   │   ├── database/       # SQLite repositories
│   │   └── loaders/        # YAML data loaders
│   └── main.py             # Application entry point
├── data/
│   ├── questions.yaml      # 44 MBTI questions
│   ├── personality_profiles.yaml  # 16 personality profiles
│   └── personality_test.db # SQLite database (created on first run)
├── docs/
│   └── plans/              # Design documentation
├── .env                     # Environment configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Architecture

The bot follows Clean Architecture principles:

- **Domain Layer**: Core business logic, no dependencies on external concerns
- **Application Layer**: Use cases orchestrating domain logic
- **Infrastructure Layer**: External integrations (Discord, Database, File I/O)

This design makes the code:
- Testable
- Maintainable
- Independent of frameworks
- Easy to migrate (e.g., to Turso DB)

## Database

The bot uses SQLite for local development. Tables:

- `users`: Tracks when users first/last took the test
- `test_sessions`: Active and completed test sessions
- `test_results`: Historical test results

Database is automatically created on first run at `./data/personality_test.db`

## Migration to Turso (Future)

To migrate to Turso DB:
1. Update `DATABASE_PATH` in `.env` to your Turso connection string
2. Install `libsql-client`: `pip install libsql-client`
3. Update database connection code to use Turso client
4. No schema changes needed (Turso is SQLite-compatible)

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
- Ensure `data/` directory exists
- Check file permissions
- Delete `personality_test.db` to recreate from scratch

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
pytest
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/
```

## License

This project is for personal/ministry use.

## Credits

Built with Clean Architecture principles using:
- discord.py
- pydantic
- aiosqlite
- PyYAML
