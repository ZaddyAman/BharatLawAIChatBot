#!/usr/bin/env python3
import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'sql_app.db')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if judgments table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='judgments'")
    if cursor.fetchone():
        print("[SUCCESS] Judgments table exists")

        # Get sample data
        cursor.execute("SELECT year, judgment_date, case_title FROM judgments LIMIT 5")
        rows = cursor.fetchall()

        print(f"\n[DATA] Sample judgment data ({len(rows)} records):")
        for i, row in enumerate(rows, 1):
            year, judgment_date, case_title = row
            print(f"{i}. Year: {year} (type: {type(year).__name__})")
            print(f"   Date: {judgment_date}")
            print(f"   Title: {case_title[:60]}{'...' if len(case_title) > 60 else ''}")
            print()

        # Check distinct years
        cursor.execute("SELECT DISTINCT year FROM judgments ORDER BY year")
        years = [row[0] for row in cursor.fetchall()]
        print(f"[YEARS] Available years in database: {years[:10]}{'...' if len(years) > 10 else ''}")

        # Check for records with year = 0
        cursor.execute("SELECT COUNT(*) FROM judgments WHERE year = 0")
        zero_year_count = cursor.fetchone()[0]
        print(f"[YEARS] Records with year = 0: {zero_year_count}")

        # Check date formats
        cursor.execute("SELECT DISTINCT judgment_date FROM judgments LIMIT 10")
        dates = [row[0] for row in cursor.fetchall()]
        print(f"[DATES] Sample judgment date formats: {dates}")

        # Check for empty dates
        cursor.execute("SELECT COUNT(*) FROM judgments WHERE judgment_date = '' OR judgment_date IS NULL")
        empty_date_count = cursor.fetchone()[0]
        print(f"[DATES] Records with empty judgment dates: {empty_date_count}")

        # Test year filtering
        cursor.execute("SELECT COUNT(*) FROM judgments WHERE year = 1950")
        year_1950_count = cursor.fetchone()[0]
        print(f"[FILTER] Records from 1950: {year_1950_count}")

        # Test sorting by date
        cursor.execute("SELECT judgment_date FROM judgments WHERE judgment_date != '' ORDER BY judgment_date LIMIT 5")
        sorted_dates = [row[0] for row in cursor.fetchall()]
        print(f"[SORT] First 5 sorted judgment dates: {sorted_dates}")

        # Check acts data structure
        print(f"\n[ACTS] Checking acts data structure...")
        try:
            # Since acts are loaded from files, let's check if we can access the data
            import os
            acts_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'annotatedCentralActs')
            if os.path.exists(acts_dir):
                json_files = [f for f in os.listdir(acts_dir) if f.endswith('.json')]
                print(f"[ACTS] Found {len(json_files)} act files")

                if json_files:
                    import json
                    sample_file = os.path.join(acts_dir, json_files[0])
                    with open(sample_file, 'r', encoding='utf-8') as f:
                        sample_act = json.load(f)
                        print(f"[ACTS] Sample act structure:")
                        print(f"  - Title: {sample_act.get('Act Title', 'N/A')}")
                        print(f"  - Enactment Date: {sample_act.get('Enactment Date', 'N/A')}")
                        print(f"  - Has Parts: {'Parts' in sample_act}")
                        print(f"  - Has Sections: {'Sections' in sample_act}")
            else:
                print(f"[ACTS] Acts directory not found: {acts_dir}")
        except Exception as e:
            print(f"[ACTS] Error checking acts: {e}")

    else:
        print("[ERROR] Judgments table does not exist")

    conn.close()
else:
    print("[ERROR] Database file not found")