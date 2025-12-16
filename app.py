from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import atexit
from datetime import datetime

from config import Config
from database import Database
from ctfd_client import CTFdClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Security headers
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com;"
    )
    return response

# Global variables
db = None
ctfd_client = None
last_update_time = None

def init_clients():
    """Initialize database and CTFd client"""
    global db, ctfd_client
    if db is None:
        db = Database()
    if ctfd_client is None:
        ctfd_client = CTFdClient()

def update_scoreboard():
    """Fetch scoreboard data from CTFd API and update database"""
    global last_update_time
    try:
        init_clients()
        logger.info("Starting scoreboard update...")
        
        # Fetch scoreboard data from CTFd
        scoreboard_data = ctfd_client.get_scoreboard(count=Config.TOP_TEAMS_COUNT)
        
        # Upsert data into database
        db.upsert_scoreboard(scoreboard_data)
        
        last_update_time = datetime.now()
        logger.info(f"Scoreboard updated successfully at {last_update_time}")
        
    except Exception as e:
        logger.error(f"Error updating scoreboard: {e}")

@app.route('/')
def index():
    """Main scoreboard page with countdown support"""
    try:
        # Check if CTF has started
        start_time = Config.get_ctf_start_time()
        if start_time is not None and not Config.is_ctf_started():
            # Show countdown page
            return render_template(
                'countdown.html',
                event_name=Config.CTFD_EVENT_NAME,
                start_time=start_time.strftime('%Y-%m-%d %H:%M:%S'),
                start_time_iso=start_time.isoformat()
            )
        
        # CTF has started, show scoreboard
        init_clients()
        # Get scoreboard data from database
        scoreboard = db.get_scoreboard(limit=Config.TOP_TEAMS_COUNT)
        
        return render_template(
            'index.html',
            event_name=Config.CTFD_EVENT_NAME,
            scoreboard=scoreboard,
            refresh_interval=Config.REFRESH_INTERVAL,
            last_update=last_update_time
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/api/scoreboard')
def api_scoreboard():
    """API endpoint to get scoreboard data as JSON"""
    try:
        init_clients()
        scoreboard = db.get_scoreboard(limit=Config.TOP_TEAMS_COUNT)
        return jsonify({
            'success': True,
            'data': scoreboard,
            'last_update': last_update_time.isoformat() if last_update_time else None
        })
    except Exception as e:
        logger.error(f"Error in API scoreboard endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/team/<int:team_id>')
def team_profile(team_id):
    """Team profile page showing team details and solves"""
    try:
        init_clients()

        # Fetch team details from CTFd API
        team_details = ctfd_client.get_team_details(team_id)

        # Fetch team solves
        team_solves = ctfd_client.get_team_solves(team_id)

        # Get team's rank from scoreboard
        scoreboard = db.get_scoreboard(limit=Config.TOP_TEAMS_COUNT)
        team_rank = None
        team_score = None
        for entry in scoreboard:
            if entry['team_id'] == team_id:
                team_rank = entry['rank']
                team_score = entry['score']
                break

        return render_template(
            'team_profile.html',
            event_name=Config.CTFD_EVENT_NAME,
            team=team_details,
            solves=team_solves,
            rank=team_rank,
            score=team_score
        )
    except Exception as e:
        logger.error(f"Error rendering team profile page: {e}")
        return render_template('error.html', error=f"Failed to load team profile: {str(e)}"), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'last_update': last_update_time.isoformat() if last_update_time else None
    })

def init_scheduler():
    """Initialize the background scheduler for periodic updates"""
    # Check if freeze mode is enabled
    if Config.FREEZE_MODE:
        logger.info("Freeze mode is enabled - scheduler will not be started")
        logger.info("Scoreboard will serve data from database only")
        return
    
    scheduler = BackgroundScheduler()
    
    # Schedule the update_scoreboard function
    trigger = IntervalTrigger(seconds=Config.REFRESH_INTERVAL)
    scheduler.add_job(
        func=update_scoreboard,
        trigger=trigger,
        id='update_scoreboard',
        name='Update scoreboard from CTFd API',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"Scheduler started with interval: {Config.REFRESH_INTERVAL} seconds")
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    # Run initial update
    update_scoreboard()

if __name__ == '__main__':
    try:
        # Check for deprecated gotrue package
        try:
            import importlib.util
            if importlib.util.find_spec("gotrue") is not None:
                logger.warning("=" * 60)
                logger.warning("DEPRECATED PACKAGE DETECTED!")
                logger.warning("The 'gotrue' package is installed but deprecated.")
                logger.warning("This may cause 'proxy' errors with Supabase.")
                logger.warning("Please run: pip uninstall gotrue -y")
                logger.warning("Or use the cleanup script: ./cleanup_deps.sh")
                logger.warning("=" * 60)
        except Exception:
            pass  # Ignore if we can't check
        
        # Validate configuration
        Config.validate()
        
        # Initialize clients
        init_clients()
        
        # Initialize scheduler
        init_scheduler()
        
        # Run Flask app
        logger.info(f"Starting Flask app on {Config.HOST}:{Config.PORT}")
        app.run(host=Config.HOST, port=Config.PORT, debug=(Config.ENV == 'development'))
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
