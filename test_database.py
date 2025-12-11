#!/usr/bin/env python3
"""
Comprehensive test suite for Database operations (database.py)
Tests Supabase integration, upsertion logic, and data retrieval
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
import hashlib
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set mock environment variables
os.environ['CTFD_API_URL'] = 'https://test.ctfd.io/api/v1'
os.environ['CTFD_API_KEY'] = 'test_api_key'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test_supabase_key'
os.environ['FLASK_SECRET_KEY'] = 'test_secret'

from database import Database


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client"""
    with patch('database.create_client') as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        yield mock_client


class TestDatabaseInitialization:
    """Test Database class initialization"""
    
    def test_database_initialization(self, mock_supabase_client):
        """Test that Database initializes with Supabase client"""
        db = Database()
        
        assert db.client is not None
        assert db.client == mock_supabase_client
    
    def test_database_uses_correct_credentials(self):
        """Test that Database uses correct Supabase credentials"""
        with patch('database.create_client') as mock_create:
            Database()
            
            mock_create.assert_called_once_with(
                'https://test.supabase.co',
                'test_supabase_key'
            )


class TestUpsertScoreboard:
    """Test upsert_scoreboard method"""
    
    def test_upsert_with_dict_entries(self, mock_supabase_client):
        """Test upserting scoreboard data with dictionary entries"""
        # Setup mock
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        db = Database()
        
        # Test data
        scoreboard_data = [
            {'account_id': 1, 'name': 'Team Alpha', 'score': 1000},
            {'account_id': 2, 'name': 'Team Beta', 'score': 800},
            {'account_id': 3, 'name': 'Team Gamma', 'score': 600}
        ]
        
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify upsert was called
        mock_table.upsert.assert_called_once()
        
        # Verify the data structure
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        assert len(records) == 3
        assert records[0]['rank'] == 1
        assert records[0]['team_id'] == 1
        assert records[0]['team_name'] == 'Team Alpha'
        assert records[0]['score'] == 1000
        assert records[2]['rank'] == 3
    
    def test_upsert_with_string_entries(self, mock_supabase_client):
        """Test upserting scoreboard data with string entries"""
        # Setup mock
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        db = Database()
        
        # Test data - string entries only
        scoreboard_data = ['Team Alpha', 'Team Beta', 'Team Gamma']
        
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify upsert was called
        mock_table.upsert.assert_called_once()
        
        # Verify the data structure
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        assert len(records) == 3
        assert records[0]['rank'] == 1
        assert records[0]['team_name'] == 'Team Alpha'
        assert records[0]['score'] == 0  # Default score for string entries
        
        # Verify team_id is a hash
        expected_hash = int(hashlib.sha256('Team Alpha'.encode()).hexdigest()[:8], 16)
        assert records[0]['team_id'] == expected_hash
    
    def test_upsert_with_mixed_entries(self, mock_supabase_client):
        """Test upserting with mixed dict and string entries"""
        # Setup mock
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        db = Database()
        
        # Mixed data
        scoreboard_data = [
            {'account_id': 1, 'name': 'Team Dict', 'score': 500},
            'Team String',
            {'account_id': 3, 'name': 'Another Dict', 'score': 300}
        ]
        
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify data structure
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        assert len(records) == 3
        assert records[0]['team_id'] == 1
        assert records[0]['team_name'] == 'Team Dict'
        assert records[1]['team_name'] == 'Team String'
        assert records[2]['team_id'] == 3
    
    def test_upsert_with_empty_data(self, mock_supabase_client):
        """Test upserting with empty data list"""
        db = Database()
        
        # Should not raise an exception
        result = db.upsert_scoreboard([])
        
        # Should not call upsert on empty data
        mock_supabase_client.table.assert_not_called()
    
    def test_upsert_with_none(self, mock_supabase_client):
        """Test upserting with None"""
        db = Database()
        
        # Should not raise an exception
        result = db.upsert_scoreboard(None)
        
        # Should not call upsert on None
        mock_supabase_client.table.assert_not_called()
    
    def test_upsert_with_large_team_ids(self, mock_supabase_client):
        """Test upserting with large team IDs (> 2^31-1)"""
        # Setup mock
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        db = Database()
        
        # Test data with large IDs that would overflow 32-bit integers
        scoreboard_data = [
            {'account_id': 3564330554, 'name': 'Team Overflow', 'score': 2000},
            {'account_id': 4294967295, 'name': 'Team MaxUint32', 'score': 1500}
        ]
        
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify large IDs are preserved
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        assert records[0]['team_id'] == 3564330554
        assert records[1]['team_id'] == 4294967295
    
    def test_upsert_conflict_on_team_id(self, mock_supabase_client):
        """Test that upsert uses team_id for conflict resolution"""
        # Setup mock
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        db = Database()
        
        scoreboard_data = [
            {'account_id': 1, 'name': 'Team One', 'score': 100}
        ]
        
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify on_conflict parameter
        call_kwargs = mock_table.upsert.call_args[1]
        assert call_kwargs['on_conflict'] == 'team_id'
    
    def test_upsert_with_missing_fields(self, mock_supabase_client):
        """Test upserting with entries missing optional fields"""
        # Setup mock
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        db = Database()
        
        # Data with missing fields
        scoreboard_data = [
            {'account_id': 1},  # Missing name and score
            {'name': 'Only Name'},  # Missing account_id and score
            {'score': 500}  # Missing account_id and name
        ]
        
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify it handles missing fields with defaults
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        assert len(records) == 3
        # First entry: has account_id but missing name/score
        assert records[0]['team_id'] == 1
        assert records[0]['team_name'] == 'Team 1'  # Default name
        assert records[0]['score'] == 0  # Default score
    
    def test_upsert_ranks_correctly(self, mock_supabase_client):
        """Test that ranks are assigned correctly starting from 1"""
        # Setup mock
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        db = Database()
        
        scoreboard_data = [
            {'account_id': 1, 'name': 'First', 'score': 1000},
            {'account_id': 2, 'name': 'Second', 'score': 900},
            {'account_id': 3, 'name': 'Third', 'score': 800},
            {'account_id': 4, 'name': 'Fourth', 'score': 700}
        ]
        
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify ranks
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        assert records[0]['rank'] == 1
        assert records[1]['rank'] == 2
        assert records[2]['rank'] == 3
        assert records[3]['rank'] == 4
    
    def test_upsert_hash_collision_different_teams(self, mock_supabase_client):
        """Test that different team names generate different hashes"""
        # Setup mock
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        db = Database()
        
        # Different team names should have different hashes
        scoreboard_data = ['Team Alpha', 'Team Beta', 'Team Gamma']
        
        db.upsert_scoreboard(scoreboard_data)
        
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        team_ids = [record['team_id'] for record in records]
        
        # All team_ids should be unique
        assert len(team_ids) == len(set(team_ids))
    
    def test_upsert_error_handling(self, mock_supabase_client):
        """Test error handling in upsert_scoreboard"""
        # Setup mock to raise exception
        mock_table = MagicMock()
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.side_effect = Exception("Database error")
        
        db = Database()
        
        scoreboard_data = [{'account_id': 1, 'name': 'Team', 'score': 100}]
        
        # Should raise the exception
        with pytest.raises(Exception) as exc_info:
            db.upsert_scoreboard(scoreboard_data)
        
        assert "Database error" in str(exc_info.value)
    
    def test_upsert_with_invalid_entry_type(self, mock_supabase_client):
        """Test handling of invalid entry types (not dict or string)"""
        # Setup mock
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        db = Database()
        
        # Mixed data with invalid types
        scoreboard_data = [
            {'account_id': 1, 'name': 'Valid Team', 'score': 100},
            12345,  # Invalid: integer
            ['invalid', 'list'],  # Invalid: list
            None,  # Invalid: None
            'Valid String Team'
        ]
        
        db.upsert_scoreboard(scoreboard_data)
        
        # Should skip invalid entries
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        # Should only have 2 valid records (dict and string)
        assert len(records) == 2
        assert records[0]['team_name'] == 'Valid Team'
        assert records[1]['team_name'] == 'Valid String Team'


class TestGetScoreboard:
    """Test get_scoreboard method"""
    
    def test_get_scoreboard_without_limit(self, mock_supabase_client):
        """Test getting scoreboard without limit"""
        # Setup mock
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_order = MagicMock()
        mock_execute = MagicMock()
        
        mock_data = [
            {'rank': 1, 'team_id': 1, 'team_name': 'Team Alpha', 'score': 1000},
            {'rank': 2, 'team_id': 2, 'team_name': 'Team Beta', 'score': 800}
        ]
        mock_execute.execute.return_value = MagicMock(data=mock_data)
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.order.return_value = mock_execute
        
        db = Database()
        result = db.get_scoreboard()
        
        assert len(result) == 2
        assert result[0]['team_name'] == 'Team Alpha'
        assert result[0]['score'] == 1000
        
        # Verify order by rank ascending
        mock_select.order.assert_called_once_with('rank', desc=False)
    
    def test_get_scoreboard_with_limit(self, mock_supabase_client):
        """Test getting scoreboard with limit"""
        # Setup mock
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_order = MagicMock()
        mock_limit = MagicMock()
        mock_execute = MagicMock()
        
        mock_data = [
            {'rank': 1, 'team_id': 1, 'team_name': 'Team Alpha', 'score': 1000}
        ]
        mock_execute.execute.return_value = MagicMock(data=mock_data)
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.order.return_value = mock_order
        mock_order.limit.return_value = mock_execute
        
        db = Database()
        result = db.get_scoreboard(limit=1)
        
        assert len(result) == 1
        assert result[0]['team_name'] == 'Team Alpha'
        
        # Verify limit was called
        mock_order.limit.assert_called_once_with(1)
    
    def test_get_scoreboard_empty_result(self, mock_supabase_client):
        """Test getting scoreboard with empty result"""
        # Setup mock
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_order = MagicMock()
        mock_execute = MagicMock()
        
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.order.return_value = mock_execute
        
        db = Database()
        result = db.get_scoreboard()
        
        assert result == []
    
    def test_get_scoreboard_error_handling(self, mock_supabase_client):
        """Test error handling in get_scoreboard"""
        # Setup mock to raise exception
        mock_table = MagicMock()
        mock_supabase_client.table.return_value = mock_table
        mock_table.select.side_effect = Exception("Query error")
        
        db = Database()
        result = db.get_scoreboard()
        
        # Should return empty list on error
        assert result == []
    
    def test_get_scoreboard_with_large_limit(self, mock_supabase_client):
        """Test getting scoreboard with large limit value"""
        # Setup mock
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_order = MagicMock()
        mock_limit = MagicMock()
        mock_execute = MagicMock()
        
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.order.return_value = mock_order
        mock_order.limit.return_value = mock_execute
        
        db = Database()
        db.get_scoreboard(limit=1000)
        
        # Verify limit was called with large number
        mock_order.limit.assert_called_once_with(1000)
    
    def test_get_scoreboard_ordering(self, mock_supabase_client):
        """Test that scoreboard is ordered by rank"""
        # Setup mock
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_order = MagicMock()
        mock_execute = MagicMock()
        
        mock_data = [
            {'rank': 1, 'team_id': 1, 'team_name': 'First', 'score': 1000},
            {'rank': 2, 'team_id': 2, 'team_name': 'Second', 'score': 900},
            {'rank': 3, 'team_id': 3, 'team_name': 'Third', 'score': 800}
        ]
        mock_execute.execute.return_value = MagicMock(data=mock_data)
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.order.return_value = mock_execute
        
        db = Database()
        result = db.get_scoreboard()
        
        # Verify data is in correct order
        assert result[0]['rank'] == 1
        assert result[1]['rank'] == 2
        assert result[2]['rank'] == 3
        
        # Verify order method was called correctly
        mock_select.order.assert_called_once_with('rank', desc=False)


class TestClearScoreboard:
    """Test clear_scoreboard method"""
    
    def test_clear_scoreboard_success(self, mock_supabase_client):
        """Test clearing scoreboard successfully"""
        # Setup mock
        mock_table = MagicMock()
        mock_delete = MagicMock()
        mock_neq = MagicMock()
        mock_execute = MagicMock()
        
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.delete.return_value = mock_delete
        mock_delete.neq.return_value = mock_execute
        
        db = Database()
        db.clear_scoreboard()
        
        # Verify delete was called with correct filter
        mock_delete.neq.assert_called_once_with('team_id', 0)
    
    def test_clear_scoreboard_error_handling(self, mock_supabase_client):
        """Test error handling in clear_scoreboard"""
        # Setup mock to raise exception
        mock_table = MagicMock()
        mock_supabase_client.table.return_value = mock_table
        mock_table.delete.side_effect = Exception("Delete error")
        
        db = Database()
        
        # Should raise the exception
        with pytest.raises(Exception) as exc_info:
            db.clear_scoreboard()
        
        assert "Delete error" in str(exc_info.value)


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
    
    def test_upsert_uses_scoreboard_table(self, mock_supabase_client):
        """Test that upsert uses 'scoreboard' table"""
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        db = Database()
        db.upsert_scoreboard([{'account_id': 1, 'name': 'Team', 'score': 100}])
        
        # Verify correct table name
        mock_supabase_client.table.assert_called_with('scoreboard')
    
    def test_get_uses_scoreboard_table(self, mock_supabase_client):
        """Test that get_scoreboard uses 'scoreboard' table"""
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_order = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.order.return_value = mock_execute
        
        db = Database()
        db.get_scoreboard()
        
        # Verify correct table name
        mock_supabase_client.table.assert_called_with('scoreboard')
    
    def test_clear_uses_scoreboard_table(self, mock_supabase_client):
        """Test that clear_scoreboard uses 'scoreboard' table"""
        mock_table = MagicMock()
        mock_delete = MagicMock()
        mock_neq = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.delete.return_value = mock_delete
        mock_delete.neq.return_value = mock_execute
        
        db = Database()
        db.clear_scoreboard()
        
        # Verify correct table name
        mock_supabase_client.table.assert_called_with('scoreboard')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
