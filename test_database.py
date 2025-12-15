#!/usr/bin/env python3
"""
Comprehensive test suite for Database operations (database.py)
Tests Supabase integration, upsertion logic, and data retrieval
Uses real data from .env file for integration testing
"""
import pytest
import hashlib
import os
import sys
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

from database import Database


@pytest.fixture
def db():
    """Create a real Database instance using .env configuration"""
    database = Database()
    yield database
    # Cleanup: clear test data after tests
    try:
        database.client.table('scoreboard').delete().neq('team_id', 0).execute()
    except Exception as e:
        print(f"Cleanup warning: {e}")


class TestDatabaseInitialization:
    """Test Database class initialization"""

    def test_database_initialization(self, db):
        """Test that Database initializes with Supabase client"""
        assert db.client is not None
        assert hasattr(db, 'client')

    def test_database_uses_environment_credentials(self):
        """Test that Database uses credentials from .env file"""
        db = Database()
        assert db.client is not None
        # Verify environment variables are loaded
        assert os.getenv('SUPABASE_URL') is not None
        assert os.getenv('SUPABASE_KEY') is not None


class TestUpsertScoreboard:
    """Test upsert_scoreboard method with real database"""

    def test_upsert_with_dict_entries(self, db):
        """Test upserting scoreboard data with dictionary entries"""
        # Test data
        scoreboard_data = [
            {'account_id': 1001, 'name': 'Team Alpha', 'score': 1000, 'rank': 1},
            {'account_id': 1002, 'name': 'Team Beta', 'score': 800, 'rank': 2},
            {'account_id': 1003, 'name': 'Team Gamma', 'score': 600, 'rank': 3}
        ]

        # Insert data
        response = db.upsert_scoreboard(scoreboard_data)
        assert response is not None

        # Verify data was inserted by retrieving it
        result = db.get_scoreboard(limit=10)
        assert len(result) == 3
        assert result[0]['team_name'] == 'Team Alpha'
        assert result[0]['score'] == 1000
        assert result[0]['rank'] == 1
        assert result[2]['rank'] == 3

    def test_upsert_with_string_entries(self, db):
        """Test upserting scoreboard data with string entries"""
        # Test data - string entries only
        scoreboard_data = ['Team Alpha', 'Team Beta', 'Team Gamma']

        # Insert data
        response = db.upsert_scoreboard(scoreboard_data)
        assert response is not None

        # Verify data was inserted
        result = db.get_scoreboard(limit=10)
        assert len(result) == 3
        assert result[0]['team_name'] == 'Team Alpha'
        assert result[0]['score'] == 0  # Default score for string entries
        assert result[0]['rank'] == 1

        # Verify team_id is a hash
        expected_hash = int(hashlib.sha256('Team Alpha'.encode()).hexdigest()[:8], 16)
        assert result[0]['team_id'] == expected_hash

    def test_upsert_with_mixed_entries(self, db):
        """Test upserting with mixed dict and string entries"""
        # Mixed data
        scoreboard_data = [
            {'account_id': 2001, 'name': 'Team Dict', 'score': 500, 'rank': 1},
            'Team String',
            {'account_id': 2003, 'name': 'Another Dict', 'score': 300, 'rank': 3}
        ]

        # Insert data
        response = db.upsert_scoreboard(scoreboard_data)
        assert response is not None

        # Verify data structure
        result = db.get_scoreboard(limit=10)
        assert len(result) == 3
        assert result[0]['team_id'] == 2001
        assert result[0]['team_name'] == 'Team Dict'
        assert result[1]['team_name'] == 'Team String'
        assert result[2]['team_id'] == 2003

    def test_upsert_with_empty_data(self, db):
        """Test upserting with empty data list"""
        # Should not raise an exception
        result = db.upsert_scoreboard([])
        assert result is None

    def test_upsert_with_none(self, db):
        """Test upserting with None"""
        # Should not raise an exception
        result = db.upsert_scoreboard(None)
        assert result is None

    def test_upsert_with_large_team_ids(self, db):
        """Test upserting with large team IDs (> 2^31-1)"""
        # Test data with large IDs that would overflow 32-bit integers
        scoreboard_data = [
            {'account_id': 3564330554, 'name': 'Team Overflow', 'score': 2000, 'rank': 1},
            {'account_id': 4294967295, 'name': 'Team MaxUint32', 'score': 1500, 'rank': 2}
        ]

        # Insert data
        response = db.upsert_scoreboard(scoreboard_data)
        assert response is not None

        # Verify large IDs are preserved
        result = db.get_scoreboard(limit=10)
        assert len(result) == 2
        assert result[0]['team_id'] == 3564330554
        assert result[1]['team_id'] == 4294967295

    def test_upsert_fresh_data_replaces_old(self, db):
        """Test that fresh upsert replaces old data"""
        # First insert
        scoreboard_data_1 = [
            {'account_id': 5001, 'name': 'Team Old', 'score': 500, 'rank': 1}
        ]
        db.upsert_scoreboard(scoreboard_data_1)

        # Second insert with fresh data
        scoreboard_data_2 = [
            {'account_id': 5002, 'name': 'Team New', 'score': 600, 'rank': 1}
        ]
        db.upsert_scoreboard(scoreboard_data_2)

        # Verify only new data exists
        result = db.get_scoreboard(limit=10)
        assert len(result) == 1
        assert result[0]['team_name'] == 'Team New'
        assert result[0]['team_id'] == 5002


class TestGetScoreboard:
    """Test get_scoreboard method"""

    def test_get_scoreboard_without_limit(self, db):
        """Test getting scoreboard without limit"""
        # Insert test data
        scoreboard_data = [
            {'account_id': 6001, 'name': 'Team One', 'score': 1000, 'rank': 1},
            {'account_id': 6002, 'name': 'Team Two', 'score': 800, 'rank': 2}
        ]
        db.upsert_scoreboard(scoreboard_data)

        result = db.get_scoreboard()

        assert len(result) == 2
        assert result[0]['team_name'] == 'Team One'
        assert result[0]['score'] == 1000
        assert result[0]['rank'] == 1
        assert result[1]['rank'] == 2

    def test_get_scoreboard_with_limit(self, db):
        """Test getting scoreboard with limit"""
        # Insert test data
        scoreboard_data = [
            {'account_id': 7001, 'name': 'Team A', 'score': 1000, 'rank': 1},
            {'account_id': 7002, 'name': 'Team B', 'score': 900, 'rank': 2},
            {'account_id': 7003, 'name': 'Team C', 'score': 800, 'rank': 3}
        ]
        db.upsert_scoreboard(scoreboard_data)

        result = db.get_scoreboard(limit=2)

        assert len(result) == 2
        assert result[0]['team_name'] == 'Team A'
        assert result[1]['team_name'] == 'Team B'

    def test_get_scoreboard_empty_result(self, db):
        """Test getting scoreboard with empty result"""
        # Ensure table is empty
        db.client.table('scoreboard').delete().neq('team_id', 0).execute()

        result = db.get_scoreboard()

        assert result == []

    def test_get_scoreboard_ordering_by_rank(self, db):
        """Test that scoreboard is ordered by rank"""
        # Insert data in random order
        scoreboard_data = [
            {'account_id': 8003, 'name': 'Third', 'score': 800, 'rank': 3},
            {'account_id': 8001, 'name': 'First', 'score': 1000, 'rank': 1},
            {'account_id': 8002, 'name': 'Second', 'score': 900, 'rank': 2}
        ]
        db.upsert_scoreboard(scoreboard_data)

        result = db.get_scoreboard()

        # Verify data is ordered by rank
        assert result[0]['rank'] == 1
        assert result[0]['team_name'] == 'First'
        assert result[1]['rank'] == 2
        assert result[1]['team_name'] == 'Second'
        assert result[2]['rank'] == 3
        assert result[2]['team_name'] == 'Third'


class TestClearScoreboard:
    """Test clear_scoreboard method"""

    def test_clear_scoreboard_success(self, db):
        """Test clearing scoreboard successfully"""
        # Insert test data
        scoreboard_data = [
            {'account_id': 9001, 'name': 'Team Clear', 'score': 500, 'rank': 1}
        ]
        db.upsert_scoreboard(scoreboard_data)

        # Verify data exists
        result_before = db.get_scoreboard()
        assert len(result_before) > 0

        # Clear scoreboard
        db.clear_scoreboard()

        # Verify data is cleared
        result_after = db.get_scoreboard()
        assert len(result_after) == 0


class TestHashGeneration:
    """Test hash generation for string team names"""

    def test_hash_consistency(self):
        """Test that hash generation is consistent"""
        team_name = "Test Team"

        # Generate hash multiple times
        hash1 = int(hashlib.sha256(team_name.encode()).hexdigest()[:8], 16)
        hash2 = int(hashlib.sha256(team_name.encode()).hexdigest()[:8], 16)

        # Should be identical
        assert hash1 == hash2

    def test_hash_uniqueness(self):
        """Test that different names generate different hashes"""
        team_names = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon']

        hashes = []
        for name in team_names:
            hash_val = int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)
            hashes.append(hash_val)

        # All hashes should be unique
        assert len(hashes) == len(set(hashes))

    def test_hash_within_bigint_range(self):
        """Test that generated hashes fit within BIGINT range"""
        max_bigint = 9223372036854775807

        team_names = ['Team' + str(i) for i in range(100)]

        for name in team_names:
            hash_val = int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)
            assert hash_val <= max_bigint

    def test_hash_can_exceed_int32(self):
        """Test that hashes can exceed 32-bit integer range"""
        max_int32 = 2147483647

        # Generate hashes until we find one that exceeds INT32
        exceeded = False
        for i in range(100):
            name = f"Team {i}"
            hash_val = int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)
            if hash_val > max_int32:
                exceeded = True
                break

        assert exceeded, "Hash values should be able to exceed INT32 range"


class TestTableName:
    """Test that correct table name is used"""

    def test_operations_use_scoreboard_table(self, db):
        """Test that database operations use the 'scoreboard' table"""
        # This is implicitly tested by all other tests
        # If wrong table name was used, tests would fail

        # Insert test data
        scoreboard_data = [
            {'account_id': 10001, 'name': 'Table Test', 'score': 100, 'rank': 1}
        ]

        # Should not raise exception if correct table is used
        response = db.upsert_scoreboard(scoreboard_data)
        assert response is not None

        # Retrieve and verify
        result = db.get_scoreboard()
        assert len(result) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

