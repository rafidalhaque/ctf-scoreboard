import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class CTFdClient:
    """Client for interacting with CTFd API"""
    
    def __init__(self):
        self.api_url = Config.CTFD_API_URL
        self.api_key = Config.CTFD_API_KEY
        self.headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_scoreboard(self, count=None):
        """
        Fetch scoreboard data from CTFd API
        
        Args:
            count: Number of top teams to fetch (optional)
            
        Returns:
            List of team/user score data
        """
        try:
            # Use the /scoreboard/top/{count} endpoint if count is specified
            if count:
                endpoint = f"{self.api_url}/scoreboard/top/{count}"
            else:
                endpoint = f"{self.api_url}/scoreboard"
            
            logger.info(f"Fetching scoreboard from: {endpoint}")
            
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # CTFd API returns data in 'data' field
            if 'data' in data:
                scoreboard_data = data['data']
            else:
                scoreboard_data = data
            
            logger.info(f"Successfully fetched {len(scoreboard_data)} scoreboard entries")
            return scoreboard_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching scoreboard from CTFd API: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching scoreboard: {e}")
            raise
    
    def test_connection(self):
        """Test connection to CTFd API"""
        try:
            response = requests.get(f"{self.api_url}/scoreboard", headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info("Successfully connected to CTFd API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to CTFd API: {e}")
            return False
