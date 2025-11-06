# Modular Command System Design

**Date:** 2025-11-06
**Status:** Approved for Implementation

## Overview

Refactor Discord bot to support modular text and slash commands with comprehensive message analytics.

## Goals

1. **Modular text commands** - Easy to add new "start test" style commands
2. **Slash commands in main.py** - Keep visible and manageable in one place
3. **Message analytics** - Store all messages for future insights
4. **Database sync** - Sync with Turso on startup

## Architecture

### Directory Structure

```
src/
├── main.py              # Bot setup, events, slash commands
├── commands/
│   ├── __init__.py
│   └── text_commands.py # Decorator registry + handlers
├── analytics/
│   ├── __init__.py
│   └── messages.py      # Message storage functions
├── database.py          # DB operations (enhanced)
└── [existing files...]
```

### Component Breakdown

#### 1. Text Command System

**Decorator-based registration** in `src/commands/text_commands.py`:

```python
_text_commands: Dict[str, Callable] = {}

def text_command(trigger: str):
    """Register text command handler."""
    def decorator(func: Callable):
        _text_commands[trigger.lower()] = func
        return func
    return decorator

async def handle_text_command(message, context) -> bool:
    """Execute command if match found."""
    content = message.content.lower().strip()
    if content in _text_commands:
        await _text_commands[content](message, context)
        return True
    return False
```

**Example command:**
```python
@text_command("start test")
async def handle_start_test(message, context):
    await context['start_test_func'](...)
```

**Benefits:**
- Add command = add decorated function
- No if/elif chains
- Self-contained handlers
- Easy to test

#### 2. Message Analytics

**Database schema** (new `messages` table):

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL UNIQUE,
    discord_user_id TEXT NOT NULL,
    discord_username TEXT NOT NULL,
    message_text TEXT NOT NULL,
    channel_id TEXT,
    channel_name TEXT,
    server_id TEXT,
    server_name TEXT,
    is_dm INTEGER NOT NULL,
    message_length INTEGER NOT NULL,
    has_attachments INTEGER NOT NULL,
    has_embeds INTEGER NOT NULL,
    has_mentions INTEGER NOT NULL,
    reply_to_message_id TEXT,
    created_at TEXT NOT NULL,
    edited_at TEXT
);

CREATE INDEX idx_messages_user ON messages(discord_user_id);
CREATE INDEX idx_messages_channel ON messages(channel_id);
CREATE INDEX idx_messages_created ON messages(created_at);
```

**Storage function** in `src/analytics/messages.py`:

```python
async def store_message(message: discord.Message) -> None:
    """Extract metadata and store in database."""
    # Extract all fields (user, channel, server, metadata)
    # Call database.save_message(data)
```

**Purpose:** Analytics only - track message patterns, active users, engagement.

#### 3. Database Updates

**Enhanced `database.py`:**

- Add `save_message()` function
- Create `messages` table in `init_database()`
- Implement sync strategy: startup sync + sync after writes

**Sync Strategy:**
- **Startup:** `db_conn.sync()` pulls latest from Turso
- **After writes:** `commit()` + `sync()` pushes to Turso
- **No periodic syncs** (keep simple)

#### 4. Main.py Integration

**Simplified `on_message` handler:**

```python
@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user or message.author.bot:
        return

    # 1. Store for analytics
    await store_message(message)

    # 2. Handle text command (if any)
    await handle_text_command(message, command_context)
```

**Command context:**

```python
command_context = {
    'start_test_func': start_test,
    'test_data': {
        'all_questions': all_questions,
        'dummy_questions': dummy_questions,
        'profiles': profiles,
        'sessions': user_sessions
    }
}
```

**Slash commands:** Stay in `async_main()` using `@tree.command` decorators.

## Migration Strategy

1. Create new directory structure
2. Implement text command system
3. Implement message analytics
4. Update database.py
5. Refactor main.py to use new systems
6. Test with existing commands

## Future Extensibility

**Adding text commands:**
```python
@text_command("new command")
async def handle_new_command(message, context):
    # implementation
```

**Adding slash commands:**
```python
@tree.command(name="new-slash", description="...")
async def new_slash_command(interaction):
    # implementation
```

**Analytics queries** can be added later to query the `messages` table.

## Success Criteria

- ✅ Existing commands work unchanged
- ✅ All messages stored in database
- ✅ Database syncs on startup
- ✅ Easy to add new text/slash commands
- ✅ Clean, readable code structure
