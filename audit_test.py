#!/usr/bin/env python3
"""
Audit script to verify two specific issues:
1. Team name is being upserted (not numerical value)
2. Score is being upserted properly
3. Database upsertion (not insertion) is working properly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock environment
os.environ['CTFD_API_URL'] = 'https://test.ctfd.io/api/v1'
os.environ['CTFD_API_KEY'] = 'test_api_key'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test_supabase_key'
os.environ['FLASK_SECRET_KEY'] = 'test_secret'

from unittest.mock import MagicMock, patch
from database import Database
import hashlib

print("=" * 70)
print("AUDIT: Checking Team Name and Score Upsertion")
print("=" * 70)

def test_issue_1_team_name_upsertion():
    """Test Issue 1: Team name is upserting correctly (not numerical value)"""
    print("\n1. Testing Team Name Upsertion (String vs Numerical)")
    print("-" * 70)
    
    with patch('database.create_client') as mock_create:
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        mock_create.return_value = mock_client
        
        db = Database()
        
        # Test with dict entries (from CTFd API)
        scoreboard_data = [
            {'account_id': 1, 'name': 'Team Alpha', 'score': 1000},
            {'account_id': 2, 'name': 'Team Beta', 'score': 800},
        ]
        
        db.upsert_scoreboard(scoreboard_data)
        
        # Check what was upserted
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        print(f"  Test Case: Dict entries from CTFd API")
        for i, record in enumerate(records):
            team_name = record['team_name']
            team_id = record['team_id']
            score = record['score']
            
            # Check if team_name is a string (not a number)
            is_string = isinstance(team_name, str)
            # Check if team_name contains actual text (not just digits)
            is_actual_name = not team_name.isdigit()
            
            print(f"    Record {i+1}:")
            print(f"      team_id: {team_id} (type: {type(team_id).__name__})")
            print(f"      team_name: '{team_name}' (type: {type(team_name).__name__})")
            print(f"      score: {score} (type: {type(score).__name__})")
            print(f"      ✓ team_name is string: {is_string}")
            print(f"      ✓ team_name is actual name (not just digits): {is_actual_name}")
            
            if not is_string or not is_actual_name:
                print(f"      ❌ ISSUE: Team name is not being upserted correctly!")
                return False
        
        print(f"\n  ✓ PASS: Team names are being upserted as strings (not numerical values)")
        return True

def test_issue_2_score_upsertion():
    """Test Issue 2: Score is upserting properly"""
    print("\n2. Testing Score Upsertion")
    print("-" * 70)
    
    with patch('database.create_client') as mock_create:
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        mock_create.return_value = mock_client
        
        db = Database()
        
        # Test with various scores
        test_cases = [
            {'account_id': 1, 'name': 'High Score Team', 'score': 9999},
            {'account_id': 2, 'name': 'Medium Score Team', 'score': 500},
            {'account_id': 3, 'name': 'Zero Score Team', 'score': 0},
            {'account_id': 4, 'name': 'No Score Key'},  # Missing score
        ]
        
        db.upsert_scoreboard(test_cases)
        
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        print(f"  Test Case: Various score values")
        for i, (test_case, record) in enumerate(zip(test_cases, records)):
            expected_score = test_case.get('score', 0)
            actual_score = record['score']
            
            print(f"    Record {i+1}: {record['team_name']}")
            print(f"      Expected score: {expected_score}")
            print(f"      Actual score: {actual_score}")
            print(f"      Match: {expected_score == actual_score}")
            
            if expected_score != actual_score:
                print(f"      ❌ ISSUE: Score mismatch!")
                return False
        
        print(f"\n  ✓ PASS: Scores are being upserted correctly")
        return True

def test_issue_3_upsertion_not_insertion():
    """Test Issue 3: Database UPSERTION (not just insertion) is working"""
    print("\n3. Testing Database Upsertion (Update or Insert)")
    print("-" * 70)
    
    with patch('database.create_client') as mock_create:
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        mock_create.return_value = mock_client
        
        db = Database()
        
        # First upsert
        initial_data = [
            {'account_id': 1, 'name': 'Team Alpha', 'score': 100},
        ]
        
        db.upsert_scoreboard(initial_data)
        
        # Check that upsert method is called (not insert)
        assert mock_table.upsert.called, "upsert method not called!"
        
        # Check on_conflict parameter
        call_kwargs = mock_table.upsert.call_args[1]
        on_conflict = call_kwargs.get('on_conflict')
        
        print(f"  Checking upsert method parameters:")
        print(f"    Method called: upsert (not insert) ✓")
        print(f"    on_conflict parameter: '{on_conflict}'")
        
        if on_conflict != 'team_id':
            print(f"    ❌ ISSUE: on_conflict should be 'team_id', got '{on_conflict}'")
            return False
        
        print(f"    ✓ on_conflict set to 'team_id' (enables upsertion)")
        
        # Second upsert with updated score (simulating an update)
        updated_data = [
            {'account_id': 1, 'name': 'Team Alpha Updated', 'score': 200},
        ]
        
        db.upsert_scoreboard(updated_data)
        
        # Verify second upsert also uses proper parameters
        call_kwargs = mock_table.upsert.call_args[1]
        assert call_kwargs.get('on_conflict') == 'team_id'
        
        print(f"\n  ✓ PASS: Database is using UPSERTION (with on_conflict='team_id')")
        print(f"    - If team_id exists: Updates the record")
        print(f"    - If team_id doesn't exist: Inserts new record")
        return True

def main():
    results = []
    
    # Run all tests
    results.append(("Team Name Upsertion", test_issue_1_team_name_upsertion()))
    results.append(("Score Upsertion", test_issue_2_score_upsertion()))
    results.append(("Database Upsertion (not Insertion)", test_issue_3_upsertion_not_insertion()))
    
    # Summary
    print("\n" + "=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Codebase is working correctly!")
    else:
        print("❌ SOME CHECKS FAILED - Issues found in codebase!")
    print("=" * 70)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
