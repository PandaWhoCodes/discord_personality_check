"""Database sync utility - ensures local replica is synced with Turso."""

import os
import sys

import libsql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def sync_database() -> None:
    """Sync local database with Turso."""
    turso_url = os.getenv("TURSO_DATABASE_URL")
    turso_token = os.getenv("TURSO_AUTH_TOKEN")

    if not turso_url or not turso_token:
        print("❌ TURSO_DATABASE_URL and TURSO_AUTH_TOKEN are required")
        sys.exit(1)

    try:
        print("🔄 Connecting to Turso database...")

        # Connect to Turso with embedded replica
        conn = libsql.connect("personality_bot.db", sync_url=turso_url, auth_token=turso_token)

        print("✅ Connected to database")

        # Force sync with remote
        print("🔄 Syncing with remote Turso database...")
        conn.sync()

        print("✅ Database synced successfully!")

        # Verify connection by running a simple query
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        print(f"\n📊 Database tables ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            print(f"  • {table_name}")

            # Get row count for each table
            try:
                count_cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = count_cursor.fetchone()[0]
                print(f"    ({count} rows)")
            except Exception:
                pass

        conn.close()
        print("\n✅ Database sync complete and verified!")

    except Exception as e:
        print(f"❌ Failed to sync database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_database()
