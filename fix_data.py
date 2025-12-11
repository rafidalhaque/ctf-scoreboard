#!/usr/bin/env python3
"""
Script to fix scoreboard data after schema migration

This script:
1. Clears existing (potentially corrupted) data from the database
2. Fetches fresh data from CTFd API
3. Inserts the fresh data into the database

Run this after migrating your database schema from INTEGER to BIGINT.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from database import Database
        from ctfd_client import CTFdClient
        from config import Config
        
        print("=" * 60)
        print("CTF Scoreboard - Data Refresh Tool")
        print("=" * 60)
        print()
        print("This script will:")
        print("1. Clear existing data from the database")
        print("2. Fetch fresh data from CTFd API")
        print("3. Insert the fresh data into the database")
        print()
        
        # Confirm before proceeding
        response = input("Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Aborted.")
            return 0
        
        print("\n" + "=" * 60)
        print("Step 1: Clearing existing database data...")
        print("=" * 60)
        
        db = Database()
        try:
            db.clear_scoreboard()
            print("✓ Successfully cleared existing data")
        except Exception as e:
            print(f"✗ Error clearing data: {e}")
            print("You may continue if this is just an empty table.")
        
        print("\n" + "=" * 60)
        print("Step 2: Fetching fresh data from CTFd API...")
        print("=" * 60)
        
        ctfd = CTFdClient()
        try:
            scoreboard_data = ctfd.get_scoreboard(count=Config.TOP_TEAMS_COUNT)
            print(f"✓ Successfully fetched {len(scoreboard_data)} records from API")
            
            # Display sample data
            SAMPLE_SIZE = 3
            if scoreboard_data:
                print("\nSample of fetched data:")
                for i, entry in enumerate(scoreboard_data[:SAMPLE_SIZE], 1):
                    if isinstance(entry, dict):
                        print(f"  {i}. {entry.get('name', 'Unknown')} - {entry.get('score', 0)} points")
                    else:
                        print(f"  {i}. {entry}")
        except Exception as e:
            print(f"✗ Error fetching from API: {e}")
            return 1
        
        print("\n" + "=" * 60)
        print("Step 3: Inserting fresh data into database...")
        print("=" * 60)
        
        try:
            db.upsert_scoreboard(scoreboard_data)
            print(f"✓ Successfully inserted {len(scoreboard_data)} records")
        except Exception as e:
            print(f"✗ Error inserting data: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        print("\n" + "=" * 60)
        print("Verification")
        print("=" * 60)
        
        # Verify data was inserted correctly
        stored_data = db.get_scoreboard(limit=5)
        print(f"\nDatabase now contains {len(stored_data)} records (showing first 5):")
        
        for entry in stored_data[:5]:
            print(f"  Rank {entry.get('rank')}: {entry.get('team_name')} - {entry.get('score')} points")
        
        print("\n" + "=" * 60)
        print("✓ Data refresh completed successfully!")
        print("=" * 60)
        print()
        print("You can now restart your application and the scoreboard should display correctly.")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
