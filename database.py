from supabase import create_client, Client
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database operations using Supabase"""
    
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    def upsert_scoreboard(self, scoreboard_data):
        """
        Upsert scoreboard data into the database
        
        Args:
            scoreboard_data: List of team/user score dictionaries or strings
        """
        try:
            if not scoreboard_data:
                logger.warning("No scoreboard data to upsert")
                return
            
            # Transform data for database
            records = []
            for idx, entry in enumerate(scoreboard_data, 1):
                # Handle both dict and string entries
                if isinstance(entry, dict):
                    # Full team data with details
                    record = {
                        'rank': idx,
                        'team_id': entry.get('account_id', idx),
                        'team_name': entry.get('name', f'Team {idx}'),
                        'score': entry.get('score', 0),
                        'updated_at': 'now()'
                    }
                elif isinstance(entry, str):
                    # String entry (just team name)
                    record = {
                        'rank': idx,
                        'team_id': idx,
                        'team_name': entry,
                        'score': 0,
                        'updated_at': 'now()'
                    }
                else:
                    logger.warning(f"Unexpected entry type at index {idx}: {type(entry)}")
                    continue
                
                records.append(record)
            
            # Upsert data (insert or update if team_id exists)
            response = self.client.table('scoreboard').upsert(
                records,
                on_conflict='team_id'
            ).execute()
            
            logger.info(f"Successfully upserted {len(records)} scoreboard records")
            return response
            
        except Exception as e:
            logger.error(f"Error upserting scoreboard data: {e}")
            raise
    
    def get_scoreboard(self, limit=None):
        """
        Retrieve scoreboard data from database
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of scoreboard records ordered by rank
        """
        try:
            query = self.client.table('scoreboard').select('*').order('rank', desc=False)
            
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Error retrieving scoreboard data: {e}")
            return []
    
    def clear_scoreboard(self):
        """Clear all scoreboard data"""
        try:
            response = self.client.table('scoreboard').delete().neq('team_id', 0).execute()
            logger.info("Cleared scoreboard data")
            return response
        except Exception as e:
            logger.error(f"Error clearing scoreboard data: {e}")
            raise
