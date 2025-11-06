# Discord MBTI Personality Bot - AI Assistant Context

## Project Overview

A Discord bot that administers MBTI personality tests through interactive button-based questions, stores results in a Turso database, and provides biblical character alignments and ministry suggestions.

**Tech Stack:**
- Python 3.11
- discord.py 2.3.0+
- Turso (libSQL) for database
- Pre-commit + Black for code quality
- Async/await architecture

## Architecture

### Modular Command System

The bot uses a **modular, decorator-based command system** for easy extensibility:

```
src/
├── main.py                 # Bot initialization, event loop (195 lines)
├── commands/
│   ├── text_commands.py   # Decorator-based text command handlers
│   └── slash_commands.py  # Slash command registration function
├── analytics/
│   └── messages.py        # Message storage for analytics
├── database.py            # Turso database operations + sync
├── models.py              # Data models (UserSession, PersonalityProfile)
└── personality.py         # Question loading, test logic, button UI
```

### Key Design Patterns

**1. Text Commands (Decorator Pattern)**
```python
# src/commands/text_commands.py
@text_command("start test")
async def handle_start_test(message, context):
    # Handler implementation
```

**2. Slash Commands (Registration Function)**
```python
# src/commands/slash_commands.py
def register_slash_commands(tree, context):
    @tree.command(name="personality", ...)
    async def personality_full(interaction):
        # Handler implementation
```

**3. Command Context**
Shared resources passed to all commands:
```python
command_context = {
    'start_test_func': start_test,  # Core test function
    'test_data': {
        'all_questions': all_questions,
        'dummy_questions': dummy_questions,
        'profiles': profiles,
        'sessions': user_sessions
    }
}
```

## Database Schema

### Table: `test_results`
Stores completed personality test results:
- `discord_user_id`, `discord_username`
- `personality_type` (MBTI type)
- `test_type` (full/dummy)
- `scores` (JSON)
- `biblical_characters`, `spiritual_gifts`, `ministry_suggestions` (JSON)
- `completed_at` (ISO timestamp)

### Table: `messages`
Analytics table for all Discord messages:
- `message_id` (unique)
- `discord_user_id`, `discord_username`
- `message_text`, `message_length`
- `channel_id`, `channel_name`, `server_id`, `server_name`
- `is_dm`, `has_attachments`, `has_embeds`, `has_mentions`
- `reply_to_message_id`
- `created_at`, `edited_at`

**Indexes:** On `discord_user_id`, `channel_id`, `created_at`

### Database Sync Strategy
- **Startup:** `db_conn.sync()` pulls latest from Turso
- **After writes:** `commit()` + `sync()` pushes to Turso
- No periodic background syncs (keeps simple)

## Core Flows

### Message Handling Flow
```python
on_message(message)
  ↓
1. Store message for analytics (all messages)
  ↓
2. Check text command registry
  ↓
3. Execute handler if match found
```

### Test Administration Flow
```python
/personality or "start test"
  ↓
1. Create UserSession
  ↓
2. Send first question with buttons (QuestionView)
  ↓
3. User clicks button → on_button_click
  ↓
4. Store answer, send next question
  ↓
5. After all questions → calculate MBTI
  ↓
6. Save to database + send results
```

## Environment Variables

Required in `.env`:
```bash
DISCORD_BOT_TOKEN=...
DISCORD_APP_ID=...
DISCORD_PUBLIC_KEY=...
TURSO_DATABASE_URL=libsql://...
TURSO_AUTH_TOKEN=...
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

## Development Setup

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run bot
python -m src.main

# Run tests
python test_modular_setup.py

# Format code
black src/ --line-length=100
pre-commit run --all-files
```

## Code Quality

**Pre-commit hooks enforce:**
- Black formatting (100 char line length)
- No trailing whitespace
- Files end with newline
- No large files (>1MB)
- No private keys
- Valid Python syntax
- No debug statements
- Valid YAML/JSON

**Configuration:** See [.pre-commit-config.yaml](.pre-commit-config.yaml) and [pyproject.toml](pyproject.toml)

## Adding New Commands

### Text Command
Edit `src/commands/text_commands.py`:
```python
@text_command("hello")
async def handle_hello(message, context):
    await message.channel.send("Hi there!")
```

### Slash Command
Edit `src/commands/slash_commands.py`, add inside `register_slash_commands()`:
```python
@tree.command(name="hello", description="Say hello")
async def hello(interaction):
    await interaction.response.send_message("Hi!")
```

**main.py never needs to change!**

## Key Files Reference

### [src/main.py](src/main.py)
- Bot initialization
- SSL connector setup (macOS compatibility)
- `start_test()` function (shared by text + slash commands)
- Event handlers: `on_ready`, `on_message`

### [src/commands/text_commands.py](src/commands/text_commands.py)
- `_text_commands` registry (dict)
- `@text_command` decorator
- `handle_text_command()` dispatcher
- Text command handlers

### [src/commands/slash_commands.py](src/commands/slash_commands.py)
- `register_slash_commands()` function
- All slash command definitions

### [src/analytics/messages.py](src/analytics/messages.py)
- `store_message()` - Extracts metadata and saves to DB

### [src/database.py](src/database.py)
- `init_database()` - Connect + create tables + sync
- `save_message()` - Insert message analytics
- `save_test_result()` - Insert test results
- `close_database()` - Cleanup

### [src/personality.py](src/personality.py)
- `load_questions()` - Load from data/questions.yaml
- `load_profiles()` - Load from data/personality_profiles.yaml
- `QuestionView` - Discord UI with buttons
- Question/answer logic

### [src/models.py](src/models.py)
- `UserSession` - Track in-progress tests
- `PersonalityProfile` - MBTI profile data
- `Question`, `Option` - Test structure

## Important Notes

### SSL Certificate Handling (macOS)
Uses `certifi` package for SSL certificates. See `create_ssl_connector()` in main.py.

### User Sessions
In-memory dict `user_sessions` tracks active tests. Not persisted - lost on bot restart.

### DM Strategy
Personality tests are sent via DM to keep channels clean. Requires users to have DMs enabled.

### Message Intents
**CRITICAL:** Bot requires `MESSAGE CONTENT INTENT` enabled in Discord Developer Portal for message reading.

### Button Interactions
Uses `discord.ui.View` and `discord.ui.Button` for interactive questions. Buttons have 15-minute timeout.

## Common Tasks

### Query Message Analytics
```python
# Get all messages from a user
SELECT * FROM messages WHERE discord_user_id = '123456789';

# Get channel activity
SELECT channel_name, COUNT(*) as msg_count
FROM messages
GROUP BY channel_id
ORDER BY msg_count DESC;

# Get messages in date range
SELECT * FROM messages
WHERE created_at BETWEEN '2025-01-01' AND '2025-01-31';
```

### Add New Personality Profile
Edit `data/personality_profiles.yaml`:
```yaml
INTJ:
  description: "The Architect"
  biblical_characters: ["Moses", "Paul"]
  spiritual_gifts: ["Teaching", "Leadership"]
  ministry_suggestions: ["Strategic planning", "Teaching"]
```

### Debug Test Flow
1. Check logs for `start_test()` called
2. Verify `UserSession` created
3. Check `QuestionView` sent
4. Monitor button click callbacks
5. Verify score calculation
6. Check database insert

## Testing

### Unit Tests
Currently uses `test_modular_setup.py` for import/registration checks.

**Future:** Add pytest tests for:
- Command registration
- Message storage
- MBTI calculation
- Database operations

### Manual Testing Checklist
- [ ] Text command: "start test"
- [ ] Text command: "start dummy test"
- [ ] Slash command: /personality
- [ ] Slash command: /personality-quick
- [ ] Button interactions work
- [ ] Results saved to database
- [ ] Messages stored in analytics table
- [ ] DM fallback handles Forbidden error

## Performance Considerations

### Message Storage
Every message is stored in database. For high-volume servers:
- Consider batching inserts
- Add message filtering (only store certain channels)
- Archive old messages periodically

### Database Sync
Current: Sync after every write.
**Optimization:** Could batch syncs or use background task.

### Session Management
Current: In-memory dict.
**Improvement:** Could use Redis/database for persistence across restarts.

## Troubleshooting

### Bot doesn't read messages
→ Check `MESSAGE CONTENT INTENT` enabled in Developer Portal

### SSL errors on macOS
→ Ensure `certifi` installed: `pip install certifi`

### Commands not registering
→ Check decorator syntax, restart bot, verify `tree.sync()` called

### Database sync fails
→ Verify `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` in `.env`

### Pre-commit fails
→ Run `black src/` to format, then commit again

## Future Enhancements

### Potential Features
- Analytics dashboard (most active users, channels)
- Personality type statistics
- Team compatibility analysis
- Custom question sets
- Multi-language support
- Scheduled reminders for retakes

### Technical Improvements
- Add comprehensive pytest suite
- Implement Redis for session persistence
- Add rate limiting for commands
- Create admin commands for bot management
- Add database migration system
- Implement caching for profiles/questions

## Git Workflow

```bash
# Standard commit (pre-commit runs automatically)
git add .
git commit -m "Add new feature"

# Pre-commit will format with Black and run checks
# If it reformats, just add and commit again
git add .
git commit -m "Add new feature"

# Emergency bypass (avoid if possible)
git commit --no-verify -m "hotfix"
```

## Resources

- [discord.py docs](https://discordpy.readthedocs.io/)
- [Turso docs](https://docs.turso.tech/)
- [Black formatter](https://black.readthedocs.io/)
- [Pre-commit](https://pre-commit.com/)

## Project History

**Initial Implementation:**
- Monolithic main.py with all commands inline
- Basic personality test with buttons
- SQLite database

**Refactoring (2025-11-06):**
- Extracted commands to modular system
- Added message analytics
- Migrated to Turso (libSQL)
- Implemented pre-commit + Black
- Reduced main.py from 268 → 195 lines

---

**Last Updated:** 2025-11-07
**Python Version:** 3.11
**Discord.py Version:** 2.3.0+
