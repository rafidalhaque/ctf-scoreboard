# CTF Public Scoreboard

A real-time public scoreboard for CTFd competitions built with Python Flask, Tailwind CSS, DaisyUI, and Supabase.

## Features

- 🏆 **Real-time Updates**: Automatically fetches and displays CTFd scoreboard data at configurable intervals
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- 🎨 **Modern UI**: Built with Tailwind CSS and DaisyUI for a beautiful, accessible interface
- 🔄 **Auto-refresh**: Page automatically reloads to show the latest standings
- 📊 **Database Integration**: Uses Supabase for reliable data storage and retrieval
- ⚙️ **Configurable**: All settings managed through environment variables

## Screenshots

The scoreboard features:
- Trophy icons for top 3 teams
- Team avatars and detailed information
- Real-time score updates
- Statistics cards showing total teams, refresh rate, and current leader

## Prerequisites

- Python 3.8 or higher
- Supabase account and project
- CTFd instance with API access

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rafidalhaque/ctf-scoreboard.git
   cd ctf-scoreboard
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Supabase Database**
   - Create a new project in [Supabase](https://supabase.com)
   - Go to the SQL Editor and run the contents of `schema.sql`
   - This will create the `scoreboard` table with proper indexes and policies

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your configuration:
   ```env
   # CTFd Configuration
   CTFD_EVENT_NAME=Your CTF Event Name
   CTFD_API_URL=https://your-ctfd-instance.com/api/v1
   CTFD_API_KEY=your_ctfd_api_key_here
   
   # Refresh interval in seconds (60 = 1 minute)
   REFRESH_INTERVAL=60
   
   # Flask Configuration
   FLASK_SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5000
   
   # Supabase Configuration
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_supabase_anon_key_here
   
   # Optional: Number of top teams to display
   TOP_TEAMS_COUNT=10
   ```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `CTFD_EVENT_NAME` | Name of your CTF event | No | "CTF Event" |
| `CTFD_API_URL` | CTFd API base URL (e.g., `https://ctf.example.com/api/v1`) | Yes | - |
| `CTFD_API_KEY` | CTFd API authentication token | Yes | - |
| `REFRESH_INTERVAL` | How often to fetch data (in seconds) | No | 60 |
| `FLASK_SECRET_KEY` | Flask secret key for sessions | No | Generated |
| `FLASK_ENV` | Flask environment (`development` or `production`) | No | "production" |
| `FLASK_HOST` | Host to bind the application | No | "0.0.0.0" |
| `FLASK_PORT` | Port to run the application | No | 5000 |
| `SUPABASE_URL` | Supabase project URL | Yes | - |
| `SUPABASE_KEY` | Supabase anon/public key | Yes | - |
| `TOP_TEAMS_COUNT` | Number of top teams to display | No | 10 |

### Getting CTFd API Key

1. Log in to your CTFd instance as an admin
2. Go to Settings → Access Tokens
3. Generate a new token with appropriate permissions
4. Copy the token to your `.env` file

### Getting Supabase Credentials

1. Create a project on [Supabase](https://supabase.com)
2. Go to Project Settings → API
3. Copy the "Project URL" to `SUPABASE_URL`
4. Copy the "anon public" key to `SUPABASE_KEY`

## Usage

### Running the Application

```bash
python app.py
```

The application will:
1. Validate your configuration
2. Start the background scheduler to fetch data every `REFRESH_INTERVAL` seconds
3. Launch the Flask web server
4. Be accessible at `http://localhost:5000` (or your configured host/port)

### API Endpoints

- `GET /` - Main scoreboard page (HTML)
- `GET /api/scoreboard` - Scoreboard data as JSON
- `GET /health` - Health check endpoint

### Development Mode

To run in development mode with debug features:

```bash
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python app.py
```

## Deployment

### Docker Deployment (Recommended)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run:

```bash
docker build -t ctf-scoreboard .
docker run -p 5000:5000 --env-file .env ctf-scoreboard
```

### Cloud Platforms

#### Heroku

1. Create a `Procfile`:
   ```
   web: python app.py
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set $(cat .env | xargs)
   git push heroku main
   ```

#### Railway / Render / Fly.io

These platforms auto-detect Python applications. Just:
1. Connect your repository
2. Set environment variables in the dashboard
3. Deploy

## Project Structure

```
ctf-scoreboard/
├── app.py                    # Main Flask application
├── config.py                 # Configuration management
├── database.py               # Supabase database operations
├── ctfd_client.py           # CTFd API client
├── requirements.txt          # Python dependencies
├── schema.sql               # Supabase database schema
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore rules
├── ctfd_api_swagger.json    # CTFd API documentation
├── templates/
│   ├── base.html            # Base template with Tailwind CSS
│   ├── index.html           # Main scoreboard page
│   └── error.html           # Error page
└── README.md                # This file
```

## Architecture

1. **Background Scheduler**: APScheduler runs a background job every N seconds (configurable via `REFRESH_INTERVAL`)
2. **API Client**: Fetches scoreboard data from CTFd API using the `/scoreboard` or `/scoreboard/top/{count}` endpoint
3. **Database Layer**: Upserts data into Supabase (insert new teams, update existing ones)
4. **Web Interface**: Flask serves HTML pages that display data from Supabase
5. **Auto-refresh**: Frontend automatically reloads to show latest data

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to CTFd API

**Solutions**:
- Verify `CTFD_API_URL` is correct and includes `/api/v1`
- Check that your API key is valid
- Ensure your CTFd instance is accessible from your server
- Check firewall and network settings

### Database Issues

**Problem**: Cannot connect to Supabase

**Solutions**:
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Ensure you've run the `schema.sql` to create the table
- Check Row Level Security (RLS) policies in Supabase
- Verify your Supabase project is active

### Empty Scoreboard

**Problem**: Scoreboard shows no data

**Solutions**:
- Check application logs for errors
- Verify the scheduler is running (check logs for "Scheduler started")
- Test API connection: `curl -H "Authorization: Token YOUR_KEY" YOUR_CTFD_URL/api/v1/scoreboard`
- Check if there's data in your Supabase table

### Upgrade Issues (Supabase Client Error)

**Problem**: Error: `Client.__init__() got an unexpected keyword argument 'proxy'`

**Solution**: This occurs when upgrading from an older version that had the deprecated `gotrue` package installed.

Run the cleanup script to fix:
```bash
./cleanup_deps.sh
```

Or manually:
```bash
pip uninstall gotrue -y
pip install -r requirements.txt --upgrade
```

See [UPGRADE.md](UPGRADE.md) for detailed upgrade instructions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Styled with [Tailwind CSS](https://tailwindcss.com/) and [DaisyUI](https://daisyui.com/)
- Database powered by [Supabase](https://supabase.com/)
- Designed for [CTFd](https://github.com/CTFd/CTFd) competitions