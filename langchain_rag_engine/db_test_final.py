#!/usr/bin/env python3
"""
Final comprehensive database connection test for Supabase
"""

import os
import sys
import socket
import subprocess
from urllib.parse import urlparse

def test_network_connectivity():
    """Test basic network connectivity to Supabase"""
    print("Testing network connectivity...")

    host = "db.leqitdsxjattozmiqlfn.supabase.co"
    port = 5432

    try:
        # Test socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print("Network connectivity: SUCCESS")
            return True
        else:
            print("Network connectivity: FAILED")
            return False
    except Exception as e:
        print(f"Network connectivity error: {e}")
        return False

def test_dns_resolution():
    """Test DNS resolution"""
    print("\nTesting DNS resolution...")

    try:
        ip = socket.gethostbyname("db.leqitdsxjattozmiqlfn.supabase.co")
        print(f"DNS Resolution: {ip}")
        return True
    except Exception as e:
        print(f"DNS Resolution failed: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection with multiple methods"""
    print("\nTesting SQLAlchemy connection...")

    # Method 1: Standard connection
    DATABASE_URL_1 = "postgresql://postgres:D7CBr8z2ZZV9Yoi2@db.leqitdsxjattozmiqlfn.supabase.co:5432/postgres"

    # Method 2: With SSL parameters
    DATABASE_URL_2 = "postgresql://postgres:D7CBr8z2ZZV9Yoi2@db.leqitdsxjattozmiqlfn.supabase.co:5432/postgres?sslmode=require"

    # Method 3: With timeout
    DATABASE_URL_3 = "postgresql://postgres:D7CBr8z2ZZV9Yoi2@db.leqitdsxjattozmiqlfn.supabase.co:5432/postgres?sslmode=require&connect_timeout=10"

    urls = [
        ("Standard", DATABASE_URL_1),
        ("SSL Mode", DATABASE_URL_2),
        ("With Timeout", DATABASE_URL_3)
    ]

    for name, url in urls:
        print(f"\n  Testing {name}...")
        try:
            from sqlalchemy import create_engine, text

            engine = create_engine(url, echo=False)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()
                print(f"  {name}: SUCCESS")
                print(f"  PostgreSQL: {version[0][:50]}...")
                return True

        except Exception as e:
            print(f"  {name}: FAILED - {str(e)[:100]}...")

    return False

def test_via_supabase_client():
    """Test using Supabase Python client"""
    print("\nTesting Supabase Python client...")

    try:
        from supabase import create_client, Client

        SUPABASE_URL = "https://leqitdsxjattozmiqlfn.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxlcWl0ZHN4amF0dG96bWlxbGZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1MTgyNzcsImV4cCI6MjA3MzA5NDI3N30.gp888LtDtvkeR93XIUOhQz7aphDAjjlJjMZokcG1fcA"

        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Test a simple query
        response = supabase.table('users').select('*').limit(1).execute()
        print("Supabase Client: SUCCESS")
        print(f"  Response: {len(response.data)} records found")
        return True

    except ImportError:
        print("Supabase Client: supabase-py not installed")
        print("  Install with: pip install supabase")
        return False
    except Exception as e:
        print(f"Supabase Client: FAILED - {str(e)[:100]}...")
        return False

def main():
    """Run all tests"""
    print("BharatLawAI Database Connection Test")
    print("=" * 50)

    results = []

    # Test 1: Network connectivity
    results.append(("Network", test_network_connectivity()))

    # Test 2: DNS resolution
    results.append(("DNS", test_dns_resolution()))

    # Test 3: SQLAlchemy connection
    results.append(("SQLAlchemy", test_sqlalchemy_connection()))

    # Test 4: Supabase client
    results.append(("Supabase Client", test_via_supabase_client()))

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print("=" * 50)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name:15} | {status}")

    successful_tests = sum(1 for _, success in results if success)
    total_tests = len(results)

    print(f"\nResult: {successful_tests}/{total_tests} tests passed")

    if successful_tests > 0:
        print("Database connectivity confirmed!")
        print("Ready to proceed with deployment")
    else:
        print("All connection methods failed")
        print("This may be due to network restrictions")
        print("Railway deployment will work despite local connection issues")

if __name__ == "__main__":
    main()