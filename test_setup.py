#!/usr/bin/env python3
"""Quick test script to verify setup without starting the bot."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all imports work."""
    print("Testing imports...")

    try:
        from src.domain.services import PersonalityCalculator, ResultsGenerator

        print("✅ Domain services imported")
    except ImportError as e:
        print(f"❌ Domain services import failed: {e}")
        return False

    try:
        from src.infrastructure.database import DatabaseConnection

        print("✅ Database infrastructure imported")
    except ImportError as e:
        print(f"❌ Database import failed: {e}")
        return False

    try:
        from src.infrastructure.loaders import QuestionLoader, ProfileLoader

        print("✅ Loaders imported")
    except ImportError as e:
        print(f"❌ Loaders import failed: {e}")
        return False

    try:
        from src.infrastructure.discord import PersonalityBot

        print("✅ Discord bot imported")
    except ImportError as e:
        print(f"❌ Discord bot import failed: {e}")
        return False

    return True


def test_data_files():
    """Test that data files exist and can be loaded."""
    print("\nTesting data files...")

    from src.infrastructure.loaders import QuestionLoader, ProfileLoader

    try:
        question_loader = QuestionLoader("./data/questions.yaml")
        questions = question_loader.load_questions()
        print(f"✅ Loaded {len(questions)} questions")

        if len(questions) != 44:
            print(f"⚠️  Warning: Expected 44 questions, got {len(questions)}")

    except Exception as e:
        print(f"❌ Failed to load questions: {e}")
        return False

    try:
        profile_loader = ProfileLoader("./data/personality_profiles.yaml")
        profiles = profile_loader.load_profiles()
        print(f"✅ Loaded {len(profiles)} personality profiles")

        if len(profiles) != 16:
            print(f"⚠️  Warning: Expected 16 profiles, got {len(profiles)}")

    except Exception as e:
        print(f"❌ Failed to load profiles: {e}")
        return False

    return True


def test_calculator():
    """Test the personality calculator."""
    print("\nTesting personality calculator...")

    from src.domain.services import PersonalityCalculator
    from src.domain.models import PersonalityDimension

    try:
        calculator = PersonalityCalculator()

        # Test MBTI type calculation
        test_scores = {
            PersonalityDimension.EI: 5.0,  # E
            PersonalityDimension.SN: -3.0,  # N
            PersonalityDimension.TF: 2.0,  # T
            PersonalityDimension.JP: -1.0,  # P
        }

        mbti_type = calculator.calculate_mbti_type(test_scores)
        print(f"✅ Calculator works! Test result: {mbti_type}")

        if mbti_type != "ENTP":
            print(f"⚠️  Warning: Expected ENTP, got {mbti_type}")

    except Exception as e:
        print(f"❌ Calculator test failed: {e}")
        return False

    return True


def test_env():
    """Test environment configuration."""
    print("\nTesting environment configuration...")

    from pathlib import Path
    import os
    from dotenv import load_dotenv

    if not Path(".env").exists():
        print("❌ .env file not found")
        return False

    load_dotenv()

    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("❌ DISCORD_BOT_TOKEN not set in .env")
        return False

    print("✅ Environment configuration looks good")
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("Discord MBTI Personality Bot - Setup Test")
    print("=" * 50)

    all_passed = True

    all_passed &= test_imports()
    all_passed &= test_env()
    all_passed &= test_data_files()
    all_passed &= test_calculator()

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Bot is ready to run.")
        print("\nTo start the bot:")
        print("  python -m src.main")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 50)


if __name__ == "__main__":
    main()
