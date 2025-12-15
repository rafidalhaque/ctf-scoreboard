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
            
            # Convert dictionary with rank keys to list if needed
            if isinstance(scoreboard_data, dict):
                # Sort by rank (key) and extract values
                scoreboard_list = []
                for rank_key in sorted(scoreboard_data.keys(), key=lambda x: int(x)):
                    team_data = scoreboard_data[rank_key]
                    # Ensure the rank is included in the team data
                    if isinstance(team_data, dict):
                        team_data['rank'] = int(rank_key)
                    scoreboard_list.append(team_data)
                scoreboard_data = scoreboard_list
            
            logger.info(f"Successfully fetched {len(scoreboard_data)} scoreboard entries")
            return scoreboard_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching scoreboard from CTFd API: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching scoreboard: {e}")
            raise
    
    def get_team_details(self, team_id):
        """
        Fetch detailed information about a specific team

        Args:
            team_id: The ID of the team

        Returns:
            Dictionary containing team details
        """
        try:
            endpoint = f"{self.api_url}/teams/{team_id}"
            logger.info(f"Fetching team details from: {endpoint}")

            response = requests.get(endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # CTFd API returns data in 'data' field
            if 'data' in data:
                team_data = data['data']
            else:
                team_data = data

            logger.info(f"Successfully fetched details for team {team_id}")
            return team_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching team details from CTFd API: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching team details: {e}")
            raise

    def get_team_solves(self, team_id):
        """
        Fetch the list of challenges solved by a specific team

        Args:
            team_id: The ID of the team

        Returns:
            List of solved challenges
        """
        try:
            endpoint = f"{self.api_url}/teams/{team_id}/solves"
            logger.info(f"Fetching team solves from: {endpoint}")

            response = requests.get(endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # CTFd API returns data in 'data' field
            if 'data' in data:
                solves_data = data['data']
            else:
                solves_data = data

            logger.info(f"Successfully fetched {len(solves_data) if isinstance(solves_data, list) else 0} solves for team {team_id}")
            return solves_data if isinstance(solves_data, list) else []

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching team solves from CTFd API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching team solves: {e}")
            return []

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
