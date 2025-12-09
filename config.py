import os
from dotenv import load_dotenv

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
