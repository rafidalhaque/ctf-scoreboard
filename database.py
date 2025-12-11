from supabase import create_client, Client
from config import Config
import logging
import hashlib

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
            for entry in scoreboard_data:
                # Handle both dict and string entries
                if isinstance(entry, dict):
                    # Full team data with details
                    # Use the rank from the entry if available, otherwise use id or enumerate
                    rank = entry.get('rank')
                    if rank is None:
                        rank = len(records) + 1
                    
                    # Get team_id - try 'id' first, then 'account_id'
                    team_id = entry.get('id') or entry.get('account_id')
                    if team_id is None:
                        team_id = rank
                    
                    record = {
                        'rank': rank,
                        'team_id': team_id,
                        'team_name': entry.get('name', f'Team {team_id}'),
                        'score': entry.get('score', 0)
                    }
                elif isinstance(entry, str):
                    # String entry (just team name)
                    # Use hash of team name to generate unique team_id to avoid collisions
                    team_id_hash = int(hashlib.sha256(entry.encode()).hexdigest()[:8], 16)
                    record = {
                        'rank': len(records) + 1,
                        'team_id': team_id_hash,
                        'team_name': entry,
                        'score': 0
                    }
                else:
                    logger.warning(f"Unexpected entry type: {type(entry)}")
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
