#!/usr/bin/env python3
"""
Integration test suite for CTF Scoreboard application
Tests end-to-end flow from API to database and Flask endpoints
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import os
import sys
import responses

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set mock environment variables
os.environ['CTFD_API_URL'] = 'https://test.ctfd.io/api/v1'
os.environ['CTFD_API_KEY'] = 'test_api_key'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test_supabase_key'
os.environ['FLASK_SECRET_KEY'] = 'test_secret'
os.environ['CTFD_EVENT_NAME'] = 'Test CTF Event'
os.environ['TOP_TEAMS_COUNT'] = '5'

from app import app as flask_app
from database import Database
from ctfd_client import CTFdClient


@pytest.fixture
def client():
    """Create a Flask test client"""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client"""
    with patch('database.create_client') as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        yield mock_client


class TestAPIToDatabaseFlow:
    """Test the flow from CTFd API to Database"""
    
    @responses.activate
    def test_fetch_and_upsert_flow(self, mock_supabase_client):
        """Test complete flow: fetch from API and upsert to database"""
        # Mock CTFd API response
        api_response = {
            'data': [
                {'account_id': 1, 'name': 'Team Alpha', 'score': 1000},
                {'account_id': 2, 'name': 'Team Beta', 'score': 800},
                {'account_id': 3, 'name': 'Team Gamma', 'score': 600}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard/top/10',
            json=api_response,
            status=200
        )
        
        # Mock database response
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        # Execute flow
        ctfd_client = CTFdClient()
        db = Database()
        
        # Fetch data
        scoreboard_data = ctfd_client.get_scoreboard(count=10)
        assert len(scoreboard_data) == 3
        
        # Upsert to database
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify upsert was called
        mock_table.upsert.assert_called_once()
        
        # Verify the data structure
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        assert len(records) == 3
        assert records[0]['team_name'] == 'Team Alpha'
        assert records[0]['score'] == 1000
    
    @responses.activate
    def test_fetch_and_upsert_with_string_data(self, mock_supabase_client):
        """Test flow with string-only scoreboard data"""
        # Mock CTFd API response with strings
        api_response = {
            'data': ['Team Alpha', 'Team Beta', 'Team Gamma']
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=api_response,
            status=200
        )
        
        # Mock database response
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        # Execute flow
        ctfd_client = CTFdClient()
        db = Database()
        
        # Fetch data
        scoreboard_data = ctfd_client.get_scoreboard()
        
        # Upsert to database
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify data was processed correctly
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        assert len(records) == 3
        assert all('team_id' in record for record in records)
        assert all('score' in record for record in records)
    
    @responses.activate
    def test_fetch_and_retrieve_flow(self, mock_supabase_client):
        """Test complete flow: fetch from API, upsert, then retrieve"""
        # Mock CTFd API response
        api_response = {
            'data': [
                {'account_id': 1, 'name': 'Team Alpha', 'score': 1000}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=api_response,
            status=200
        )
        
        # Mock database upsert
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_upsert_execute = MagicMock()
        mock_upsert_execute.execute.return_value = MagicMock(data=[])
        mock_table.upsert.return_value = mock_upsert_execute
        
        # Mock database retrieval
        mock_select = MagicMock()
        mock_order = MagicMock()
        mock_get_execute = MagicMock()
        stored_data = [
            {'rank': 1, 'team_id': 1, 'team_name': 'Team Alpha', 'score': 1000}
        ]
        mock_get_execute.execute.return_value = MagicMock(data=stored_data)
        mock_table.select.return_value = mock_select
        mock_select.order.return_value = mock_get_execute
        
        mock_supabase_client.table.return_value = mock_table
        
        # Execute flow
        ctfd_client = CTFdClient()
        db = Database()
        
        # Fetch and upsert
        scoreboard_data = ctfd_client.get_scoreboard()
        db.upsert_scoreboard(scoreboard_data)
        
        # Retrieve
        result = db.get_scoreboard()
        
        assert len(result) == 1
        assert result[0]['team_name'] == 'Team Alpha'
        assert result[0]['score'] == 1000


class TestFlaskAPIEndpoints:
    """Test Flask API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'last_update' in data
    
    @patch('app.db')
    def test_api_scoreboard_endpoint_success(self, mock_db, client):
        """Test /api/scoreboard endpoint with successful data"""
        # Mock database response
        mock_db.get_scoreboard.return_value = [
            {'rank': 1, 'team_id': 1, 'team_name': 'Team Alpha', 'score': 1000},
            {'rank': 2, 'team_id': 2, 'team_name': 'Team Beta', 'score': 800}
        ]
        
        response = client.get('/api/scoreboard')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'data' in data
        assert len(data['data']) == 2
        assert data['data'][0]['team_name'] == 'Team Alpha'
    
    @patch('app.db')
    def test_api_scoreboard_endpoint_empty(self, mock_db, client):
        """Test /api/scoreboard endpoint with empty scoreboard"""
        mock_db.get_scoreboard.return_value = []
        
        response = client.get('/api/scoreboard')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data'] == []
    
    @patch('app.db')
    def test_api_scoreboard_endpoint_error(self, mock_db, client):
        """Test /api/scoreboard endpoint with error"""
        mock_db.get_scoreboard.side_effect = Exception("Database error")
        
        response = client.get('/api/scoreboard')
        
        assert response.status_code == 500
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
    
    @patch('app.Config.is_ctf_started')
    @patch('app.db')
    def test_index_endpoint_scoreboard(self, mock_db, mock_is_started, client):
        """Test / endpoint when CTF has started"""
        mock_is_started.return_value = True
        mock_db.get_scoreboard.return_value = [
            {'rank': 1, 'team_id': 1, 'team_name': 'Team Alpha', 'score': 1000}
        ]
        
        response = client.get('/')
        
        assert response.status_code == 200
        # Check that response contains scoreboard content (not countdown)
        assert b'Team Alpha' in response.data or b'scoreboard' in response.data.lower()
    
    @patch('app.Config.get_ctf_start_time')
    @patch('app.Config.is_ctf_started')
    def test_index_endpoint_countdown(self, mock_is_started, mock_get_start_time, client):
        """Test / endpoint when CTF has not started yet"""
        from datetime import datetime, timedelta
        
        future_time = datetime.now() + timedelta(hours=1)
        mock_get_start_time.return_value = future_time
        mock_is_started.return_value = False
        
        response = client.get('/')
        
        assert response.status_code == 200
        # Check that response contains countdown content
        assert b'countdown' in response.data.lower() or b'start' in response.data.lower()


class TestSecurityHeaders:
    """Test security headers are applied"""
    
    def test_security_headers_present(self, client):
        """Test that security headers are present in responses"""
        response = client.get('/health')
        
        # Check for security headers
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        
        assert 'X-XSS-Protection' in response.headers
        assert response.headers['X-XSS-Protection'] == '1; mode=block'
        
        assert 'Strict-Transport-Security' in response.headers
        
        assert 'Content-Security-Policy' in response.headers
    
    def test_security_headers_on_all_routes(self, client):
        """Test that security headers are present on all routes"""
        routes_to_test = ['/health', '/api/scoreboard']
        
        for route in routes_to_test:
            response = client.get(route)
            assert 'X-Content-Type-Options' in response.headers
            assert 'X-Frame-Options' in response.headers


class TestErrorHandling:
    """Test error handling throughout the application"""
    
    @patch('app.db')
    def test_database_error_handling(self, mock_db, client):
        """Test that database errors are handled gracefully"""
        mock_db.get_scoreboard.side_effect = Exception("Connection error")
        
        response = client.get('/api/scoreboard')
        
        # Should return error response, not crash
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
    
    @responses.activate
    def test_api_connection_error_handling(self, mock_supabase_client):
        """Test handling of CTFd API connection errors"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            body=Exception("Network error")
        )
        
        ctfd_client = CTFdClient()
        
        with pytest.raises(Exception):
            ctfd_client.get_scoreboard()


class TestDataIntegrity:
    """Test data integrity throughout the application"""
    
    @responses.activate
    def test_large_ids_preserved_through_flow(self, mock_supabase_client):
        """Test that large team IDs are preserved through entire flow"""
        # Mock CTFd API with large IDs
        large_id = 3564330554
        api_response = {
            'data': [
                {'account_id': large_id, 'name': 'Team Large ID', 'score': 1000}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=api_response,
            status=200
        )
        
        # Mock database
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        # Execute flow
        ctfd_client = CTFdClient()
        db = Database()
        
        scoreboard_data = ctfd_client.get_scoreboard()
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify large ID was preserved
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        assert records[0]['team_id'] == large_id
    
    @responses.activate
    def test_ranks_assigned_correctly(self, mock_supabase_client):
        """Test that ranks are assigned correctly in order"""
        # Mock CTFd API response
        api_response = {
            'data': [
                {'account_id': 1, 'name': 'First', 'score': 1000},
                {'account_id': 2, 'name': 'Second', 'score': 900},
                {'account_id': 3, 'name': 'Third', 'score': 800}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=api_response,
            status=200
        )
        
        # Mock database
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_execute.execute.return_value = MagicMock(data=[])
        
        mock_supabase_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute
        
        # Execute flow
        ctfd_client = CTFdClient()
        db = Database()
        
        scoreboard_data = ctfd_client.get_scoreboard()
        db.upsert_scoreboard(scoreboard_data)
        
        # Verify ranks are sequential starting from 1
        call_args = mock_table.upsert.call_args
        records = call_args[0][0]
        
        assert records[0]['rank'] == 1
        assert records[1]['rank'] == 2
        assert records[2]['rank'] == 3


class TestConfigValidation:
    """Test configuration validation"""
    
    def test_config_has_required_attributes(self):
        """Test that Config has all required attributes"""
        from config import Config
        
        required_attrs = [
            'CTFD_EVENT_NAME', 'CTFD_API_URL', 'CTFD_API_KEY',
            'REFRESH_INTERVAL', 'SECRET_KEY', 'ENV', 'HOST', 'PORT',
            'SUPABASE_URL', 'SUPABASE_KEY', 'TOP_TEAMS_COUNT'
        ]
        
        for attr in required_attrs:
            assert hasattr(Config, attr), f"Missing config attribute: {attr}"
    
    def test_config_top_teams_count_is_int(self):
        """Test that TOP_TEAMS_COUNT is an integer"""
        from config import Config
        
        assert isinstance(Config.TOP_TEAMS_COUNT, int)
        assert Config.TOP_TEAMS_COUNT > 0  # Should be a positive integer


class TestUpdateScoreboardFunction:
    """Test the update_scoreboard function"""
    
    @responses.activate
    @patch('app.db')
    @patch('app.ctfd_client')
    def test_update_scoreboard_success(self, mock_ctfd, mock_db):
        """Test successful scoreboard update"""
        from app import update_scoreboard
        
        # Mock CTFd client response
        mock_ctfd.get_scoreboard.return_value = [
            {'account_id': 1, 'name': 'Team Alpha', 'score': 1000}
        ]
        
        # Mock database upsert
        mock_db.upsert_scoreboard.return_value = None
        
        # Should not raise exception
        update_scoreboard()
        
        # Verify calls were made
        mock_ctfd.get_scoreboard.assert_called_once()
        mock_db.upsert_scoreboard.assert_called_once()
    
    @patch('app.db')
    @patch('app.ctfd_client')
    def test_update_scoreboard_handles_errors(self, mock_ctfd, mock_db):
        """Test that update_scoreboard handles errors gracefully"""
        from app import update_scoreboard
        
        # Mock CTFd client to raise error
        mock_ctfd.get_scoreboard.side_effect = Exception("API error")
        
        # Should not raise exception (should be caught and logged)
        update_scoreboard()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
