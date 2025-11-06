#!/usr/bin/env python3
"""Test the new modular command system setup."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all new modules import correctly."""
    print("Testing imports...")

    try:
        from src.commands import text_command, handle_text_command

        print("✅ Text command system imported")
    except ImportError as e:
        print(f"❌ Text command import failed: {e}")
        return False

    try:
        from src.commands import register_slash_commands

        print("✅ Slash command system imported")
    except ImportError as e:
        print(f"❌ Slash command import failed: {e}")
        return False

    try:
        from src.analytics import store_message

        print("✅ Analytics module imported")
    except ImportError as e:
        print(f"❌ Analytics import failed: {e}")
        return False

    try:
        from src.database import save_message

        print("✅ Database save_message imported")
    except ImportError as e:
        print(f"❌ Database import failed: {e}")
        return False

    return True


def test_command_registration():
    """Test that text commands are registered."""
    print("\nTesting command registration...")

    from src.commands.text_commands import _text_commands

    expected_commands = ["start test", "start dummy test"]

    for cmd in expected_commands:
        if cmd in _text_commands:
            print(f"✅ Command registered: '{cmd}'")
        else:
            print(f"❌ Command NOT registered: '{cmd}'")
            return False

    print(f"✅ Total commands registered: {len(_text_commands)}")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Modular Command System - Setup Test")
    print("=" * 60)

    all_passed = True

    all_passed &= test_imports()
    all_passed &= test_command_registration()

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Modular system is ready.")
        print("\nNew structure:")
        print("  📁 src/commands/")
        print("      ├── text_commands.py     - Text command handlers")
        print("      └── slash_commands.py    - Slash command registration")
        print("  📁 src/analytics/")
        print("      └── messages.py          - Message storage")
        print("  📝 src/database.py           - Enhanced with messages table")
        print("  📝 src/main.py               - Clean bot initialization")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
