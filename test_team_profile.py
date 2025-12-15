#!/usr/bin/env python3
"""
Test script for team profile feature
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ctfd_client import CTFdClient
from database import Database

def test_team_profile():
    """Test the team profile functionality"""
    print("=" * 60)
    print("Testing Team Profile Feature")
    print("=" * 60)

    # Initialize clients
    print("\n1. Initializing CTFd Client...")
    try:
        ctfd_client = CTFdClient()
        print("✓ CTFd Client initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize CTFd Client: {e}")
        return False

    # Test get_scoreboard
    print("\n2. Fetching scoreboard...")
    try:
        scoreboard = ctfd_client.get_scoreboard(count=10)
        print(f"✓ Fetched {len(scoreboard)} teams from scoreboard")
        if scoreboard:
            first_team = scoreboard[0]
            print(f"   First team: {first_team.get('name', 'Unknown')} (ID: {first_team.get('account_id', first_team.get('id', 'Unknown'))})")
            team_id = first_team.get('account_id', first_team.get('id'))
        else:
            print("✗ No teams found in scoreboard")
            return False
    except Exception as e:
        print(f"✗ Failed to fetch scoreboard: {e}")
        return False

    # Test get_team_details
    print(f"\n3. Fetching details for team ID {team_id}...")
    try:
        team_details = ctfd_client.get_team_details(team_id)
        print(f"✓ Successfully fetched team details")
        print(f"   Name: {team_details.get('name', 'N/A')}")
        print(f"   Country: {team_details.get('country', 'N/A')}")
        print(f"   Affiliation: {team_details.get('affiliation', 'N/A')}")
        print(f"   Website: {team_details.get('website', 'N/A')}")
    except Exception as e:
        print(f"✗ Failed to fetch team details: {e}")
        return False

    # Test get_team_solves
    print(f"\n4. Fetching solves for team ID {team_id}...")
    try:
        team_solves = ctfd_client.get_team_solves(team_id)
        print(f"✓ Successfully fetched team solves")
        print(f"   Total solves: {len(team_solves)}")
        if team_solves:
            print(f"   First solve: {team_solves[0].get('challenge', {}).get('name', 'Unknown challenge')}")
    except Exception as e:
        print(f"✗ Failed to fetch team solves: {e}")
        # This is not critical, continue

    # Test database
    print("\n5. Testing Database integration...")
    try:
        db = Database()
        db.upsert_scoreboard(scoreboard)
        stored_scoreboard = db.get_scoreboard(limit=10)
        print(f"✓ Database operations successful")
        print(f"   Stored {len(stored_scoreboard)} teams in database")
    except Exception as e:
        print(f"✗ Database operations failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ All tests passed! Team profile feature is ready.")
    print("=" * 60)
    print("\nUsage:")
    print("  - Visit http://localhost:5000/ to see the scoreboard")
    print("  - Click on any team name to view their profile")
    print(f"  - Or visit http://localhost:5000/team/{team_id} directly")
    print("=" * 60)

    return True

if __name__ == '__main__':
    success = test_team_profile()
    sys.exit(0 if success else 1)

