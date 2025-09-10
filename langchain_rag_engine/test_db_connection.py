#!/usr/bin/env python3
"""
Test script to verify Supabase database connection
Run this before deploying to ensure database connectivity
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Supabase credentials from creds.md
SUPABASE_URL = "https://leqitdsxjattozmiqlfn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxlcWl0ZHN4amF0dG96bWlxbGZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1MTgyNzcsImV4cCI6MjA3MzA5NDI3N30.gp888LtDtvkeR93XIUOhQz7aphDAjjlJjMZokcG1fcA"

# Create database URL for SQLAlchemy
DATABASE_URL = f"postgresql://postgres:D7CBr8z2ZZV9Yoi2@db.leqitdsxjattozmiqlfn.supabase.co:5432/postgres"

def test_connection():
    """Test database connection and basic operations"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL, echo=True)

        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection successful!")

            # Test basic query
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()
            print(f"📊 PostgreSQL Version: {version[0]}")

            # Check if our tables exist
            tables = ['users', 'conversations', 'messages', 'judgments', 'feedback']
            for table in tables:
                result = conn.execute(text(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table}');"))
                exists = result.fetchone()[0]
                status = "✅" if exists else "❌"
                print(f"{status} Table '{table}' exists: {exists}")

            # Test inserting a sample user
            print("\n🧪 Testing data insertion...")
            conn.execute(text("""
                INSERT INTO users (email, hashed_password, full_name, is_active)
                VALUES ('test@example.com', 'hashed_password', 'Test User', true)
                ON CONFLICT (email) DO NOTHING;
            """))
            conn.commit()
            print("✅ Sample user inserted successfully!")

            # Test querying data
            result = conn.execute(text("SELECT COUNT(*) FROM users;"))
            user_count = result.fetchone()[0]
            print(f"👥 Total users in database: {user_count}")

        print("\n🎉 All database tests passed!")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🔍 Testing Supabase database connection...")
    success = test_connection()
    if success:
        print("\n✅ Database is ready for deployment!")
    else:
        print("\n❌ Please check your database configuration and try again.")