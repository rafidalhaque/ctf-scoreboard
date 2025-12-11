#!/usr/bin/env python3
"""
Comprehensive test suite for CTFd API client (ctfd_client.py)
Tests API interactions, data fetching, and error handling
"""
import pytest
import responses
import requests
from unittest.mock import Mock, patch
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set mock environment variables
os.environ['CTFD_API_URL'] = 'https://test.ctfd.io/api/v1'
os.environ['CTFD_API_KEY'] = 'test_api_key_12345'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test_supabase_key'
os.environ['FLASK_SECRET_KEY'] = 'test_secret'

from ctfd_client import CTFdClient


class TestCTFdClientInitialization:
    """Test CTFdClient initialization"""
    
    def test_client_initialization(self):
        """Test that client initializes with correct configuration"""
        client = CTFdClient()
        
        assert client.api_url == 'https://test.ctfd.io/api/v1'
        assert client.api_key == 'test_api_key_12345'
        assert 'Authorization' in client.headers
        assert client.headers['Authorization'] == 'Token test_api_key_12345'
        assert client.headers['Content-Type'] == 'application/json'
    
    def test_client_headers_format(self):
        """Test that headers are properly formatted"""
        client = CTFdClient()
        
        # Verify headers structure
        assert isinstance(client.headers, dict)
        assert len(client.headers) == 2
        assert 'Authorization' in client.headers
        assert 'Content-Type' in client.headers


class TestGetScoreboard:
    """Test get_scoreboard method"""
    
    @responses.activate
    def test_get_scoreboard_with_count(self):
        """Test fetching scoreboard with count parameter"""
        # Mock API response
        mock_response = {
            'success': True,
            'data': [
                {'account_id': 1, 'name': 'Team Alpha', 'score': 1000},
                {'account_id': 2, 'name': 'Team Beta', 'score': 800},
                {'account_id': 3, 'name': 'Team Gamma', 'score': 600}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard/top/3',
            json=mock_response,
            status=200
        )
        
        client = CTFdClient()
        result = client.get_scoreboard(count=3)
        
        assert len(result) == 3
        assert result[0]['name'] == 'Team Alpha'
        assert result[0]['score'] == 1000
        assert result[2]['name'] == 'Team Gamma'
    
    @responses.activate
    def test_get_scoreboard_without_count(self):
        """Test fetching scoreboard without count parameter"""
        mock_response = {
            'success': True,
            'data': [
                {'account_id': 1, 'name': 'Team One', 'score': 500}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=mock_response,
            status=200
        )
        
        client = CTFdClient()
        result = client.get_scoreboard()
        
        assert len(result) == 1
        assert result[0]['name'] == 'Team One'
    
    @responses.activate
    def test_get_scoreboard_with_large_team_ids(self):
        """Test handling of large team IDs (> 2^31-1)"""
        # Test with IDs that would overflow 32-bit integers
        mock_response = {
            'data': [
                {'account_id': 3564330554, 'name': 'Team Overflow', 'score': 2000},
                {'account_id': 4294967295, 'name': 'Team MaxUint32', 'score': 1500}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard/top/10',
            json=mock_response,
            status=200
        )
        
        client = CTFdClient()
        result = client.get_scoreboard(count=10)
        
        assert len(result) == 2
        assert result[0]['account_id'] == 3564330554
        assert result[1]['account_id'] == 4294967295
    
    @responses.activate
    def test_get_scoreboard_with_string_entries(self):
        """Test handling of string entries (team names only)"""
        mock_response = {
            'data': ['Team Alpha', 'Team Beta', 'Team Gamma']
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=mock_response,
            status=200
        )
        
        client = CTFdClient()
        result = client.get_scoreboard()
        
        assert len(result) == 3
        assert result[0] == 'Team Alpha'
        assert isinstance(result[1], str)
    
    @responses.activate
    def test_get_scoreboard_empty_response(self):
        """Test handling of empty scoreboard"""
        mock_response = {'data': []}
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=mock_response,
            status=200
        )
        
        client = CTFdClient()
        result = client.get_scoreboard()
        
        assert result == []
    
    @responses.activate
    def test_get_scoreboard_without_data_field(self):
        """Test handling of response without 'data' field"""
        mock_response = [
            {'account_id': 1, 'name': 'Direct Team', 'score': 100}
        ]
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=mock_response,
            status=200
        )
        
        client = CTFdClient()
        result = client.get_scoreboard()
        
        assert len(result) == 1
        assert result[0]['name'] == 'Direct Team'
    
    @responses.activate
    def test_get_scoreboard_api_error_401(self):
        """Test handling of 401 Unauthorized error"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json={'error': 'Unauthorized'},
            status=401
        )
        
        client = CTFdClient()
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_scoreboard()
    
    @responses.activate
    def test_get_scoreboard_api_error_404(self):
        """Test handling of 404 Not Found error"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json={'error': 'Not Found'},
            status=404
        )
        
        client = CTFdClient()
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_scoreboard()
    
    @responses.activate
    def test_get_scoreboard_api_error_500(self):
        """Test handling of 500 Internal Server Error"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json={'error': 'Internal Server Error'},
            status=500
        )
        
        client = CTFdClient()
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_scoreboard()
    
    @responses.activate
    def test_get_scoreboard_timeout(self):
        """Test handling of request timeout"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            body=requests.exceptions.Timeout()
        )
        
        client = CTFdClient()
        
        with pytest.raises(requests.exceptions.Timeout):
            client.get_scoreboard()
    
    @responses.activate
    def test_get_scoreboard_connection_error(self):
        """Test handling of connection error"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            body=requests.exceptions.ConnectionError()
        )
        
        client = CTFdClient()
        
        with pytest.raises(requests.exceptions.ConnectionError):
            client.get_scoreboard()
    
    @responses.activate
    def test_get_scoreboard_with_zero_scores(self):
        """Test handling of teams with zero scores"""
        mock_response = {
            'data': [
                {'account_id': 1, 'name': 'New Team', 'score': 0},
                {'account_id': 2, 'name': 'Another New Team', 'score': 0}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=mock_response,
            status=200
        )
        
        client = CTFdClient()
        result = client.get_scoreboard()
        
        assert len(result) == 2
        assert result[0]['score'] == 0
        assert result[1]['score'] == 0
    
    @responses.activate
    def test_get_scoreboard_with_negative_scores(self):
        """Test handling of negative scores (edge case)"""
        mock_response = {
            'data': [
                {'account_id': 1, 'name': 'Penalized Team', 'score': -100}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=mock_response,
            status=200
        )
        
        client = CTFdClient()
        result = client.get_scoreboard()
        
        assert result[0]['score'] == -100


class TestTestConnection:
    """Test test_connection method"""
    
    @responses.activate
    def test_connection_success(self):
        """Test successful connection to CTFd API"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json={'success': True, 'data': []},
            status=200
        )
        
        client = CTFdClient()
        result = client.test_connection()
        
        assert result is True
    
    @responses.activate
    def test_connection_failure_401(self):
        """Test connection failure with 401 error"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json={'error': 'Unauthorized'},
            status=401
        )
        
        client = CTFdClient()
        result = client.test_connection()
        
        assert result is False
    
    @responses.activate
    def test_connection_timeout(self):
        """Test connection failure due to timeout"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            body=requests.exceptions.Timeout()
        )
        
        client = CTFdClient()
        result = client.test_connection()
        
        assert result is False
    
    @responses.activate
    def test_connection_network_error(self):
        """Test connection failure due to network error"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            body=requests.exceptions.ConnectionError()
        )
        
        client = CTFdClient()
        result = client.test_connection()
        
        assert result is False


class TestAPIEndpointBuilding:
    """Test API endpoint URL construction"""
    
    @responses.activate
    def test_endpoint_with_count(self):
        """Test that endpoint is correctly built with count"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard/top/5',
            json={'data': []},
            status=200
        )
        
        client = CTFdClient()
        client.get_scoreboard(count=5)
        
        # Verify the correct endpoint was called
        assert len(responses.calls) == 1
        assert 'scoreboard/top/5' in responses.calls[0].request.url
    
    @responses.activate
    def test_endpoint_without_count(self):
        """Test that endpoint is correctly built without count"""
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json={'data': []},
            status=200
        )
        
        client = CTFdClient()
        client.get_scoreboard()
        
        # Verify the correct endpoint was called
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url.endswith('/scoreboard')
    
    def test_headers_sent_correctly(self):
        """Test that authorization headers are sent with requests"""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                'https://test.ctfd.io/api/v1/scoreboard',
                json={'data': []},
                status=200
            )
            
            client = CTFdClient()
            client.get_scoreboard()
            
            # Verify headers
            assert len(rsps.calls) == 1
            request_headers = rsps.calls[0].request.headers
            assert 'Authorization' in request_headers
            assert request_headers['Authorization'] == 'Token test_api_key_12345'
            assert request_headers['Content-Type'] == 'application/json'


class TestDataFormats:
    """Test handling of different data formats from CTFd API"""
    
    @responses.activate
    def test_mixed_data_types(self):
        """Test handling of mixed data types in response"""
        mock_response = {
            'data': [
                {'account_id': 1, 'name': 'Team Dict', 'score': 100},
                'Team String',
                {'account_id': 3, 'name': 'Another Dict', 'score': 50}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=mock_response,
            status=200
        )
        
        client = CTFdClient()
        result = client.get_scoreboard()
        
        assert len(result) == 3
        assert isinstance(result[0], dict)
        assert isinstance(result[1], str)
        assert isinstance(result[2], dict)
    
    @responses.activate
    def test_additional_fields_in_response(self):
        """Test that additional fields in API response are preserved"""
        mock_response = {
            'data': [
                {
                    'account_id': 1,
                    'name': 'Team Extra',
                    'score': 500,
                    'extra_field': 'extra_value',
                    'members': ['user1', 'user2']
                }
            ]
        }
        
        responses.add(
            responses.GET,
            'https://test.ctfd.io/api/v1/scoreboard',
            json=mock_response,
            status=200
        )
        
        client = CTFdClient()
        result = client.get_scoreboard()
        
        assert result[0]['extra_field'] == 'extra_value'
        assert 'members' in result[0]
        assert len(result[0]['members']) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
