#!/usr/bin/env python3
"""
Debug script to check what data is currently in the database
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import Database
    from ctfd_client import CTFdClient
    import json
    
    print("=" * 60)
    print("CTF Scoreboard - Data Debug")
    print("=" * 60)
    print()
    
    # Check database data
    print("Checking database contents...")
    db = Database()
    scoreboard = db.get_scoreboard()
    
    print(f"\nFound {len(scoreboard)} records in database:")
    print()
    
    for i, entry in enumerate(scoreboard[:5], 1):  # Show first 5
        print(f"Record {i}:")
        print(f"  rank: {entry.get('rank')} (type: {type(entry.get('rank'))})")
        print(f"  team_id: {entry.get('team_id')} (type: {type(entry.get('team_id'))})")
        print(f"  team_name: {entry.get('team_name')} (type: {type(entry.get('team_name'))})")
        print(f"  score: {entry.get('score')} (type: {type(entry.get('score'))})")
        print()
    
    # Check CTFd API data
    print("\n" + "=" * 60)
    print("Checking CTFd API response...")
    print("=" * 60)
    
    try:
        ctfd = CTFdClient()
        api_data = ctfd.get_scoreboard(count=5)
        
        print(f"\nFound {len(api_data)} records from API:")
        print()
        
        for i, entry in enumerate(api_data, 1):
            print(f"API Record {i}:")
            print(f"  Type: {type(entry)}")
            if isinstance(entry, dict):
                print(f"  account_id: {entry.get('account_id')} (type: {type(entry.get('account_id'))})")
                print(f"  name: {entry.get('name')} (type: {type(entry.get('name'))})")
                print(f"  score: {entry.get('score')} (type: {type(entry.get('score'))})")
            elif isinstance(entry, str):
                print(f"  Value: {entry}")
            else:
                print(f"  Value: {entry}")
            print()
            
    except Exception as e:
        print(f"Error fetching from API: {e}")
        print("This is expected if CTFd API credentials are not configured.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
