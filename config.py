import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Config:
    """Application configuration from environment variables"""
    
    # CTFd Configuration
    CTFD_EVENT_NAME = os.getenv('CTFD_EVENT_NAME', 'CTF Event')
    CTFD_API_URL = os.getenv('CTFD_API_URL')
    CTFD_API_KEY = os.getenv('CTFD_API_KEY')
    
    # Refresh interval in seconds
    REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', '60'))
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    ENV = os.getenv('FLASK_ENV', 'production')
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '5000'))
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Display Configuration
    TOP_TEAMS_COUNT = int(os.getenv('TOP_TEAMS_COUNT', '10'))
    
    # CTF Start Time Configuration
    # Note: CTF_START_TIME uses server's local timezone. Ensure server timezone is configured correctly.
    CTF_START_TIME = os.getenv('CTF_START_TIME')
    
    @classmethod
    def get_ctf_start_time(cls):
        """
        Parse and return CTF start time as datetime object.
        
        Returns:
            datetime object in server's local timezone, or None if not configured or invalid
        
        Note:
            Time is interpreted in server's local timezone. For production deployments,
            ensure the server timezone is properly configured (e.g., via TZ environment variable).
        """
        if not cls.CTF_START_TIME:
            return None
        try:
            return datetime.strptime(cls.CTF_START_TIME, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None
    
    @classmethod
    def is_ctf_started(cls):
        """
        Check if CTF has started.
        
        Returns:
            True if CTF has started or no start time is configured, False otherwise
        
        Note:
            Comparison uses server's local time. Ensure server timezone matches CTF_START_TIME timezone.
        """
        start_time = cls.get_ctf_start_time()
        if start_time is None:
            return True  # If no start time is set, assume CTF is active
        return datetime.now() >= start_time
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = [
            ('CTFD_API_URL', cls.CTFD_API_URL),
            ('CTFD_API_KEY', cls.CTFD_API_KEY),
            ('SUPABASE_URL', cls.SUPABASE_URL),
            ('SUPABASE_KEY', cls.SUPABASE_KEY),
        ]
        
        missing = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
