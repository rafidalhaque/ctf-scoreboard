# Quick Start Guide

Get your CTFd Public Scoreboard up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- CTFd instance with API access
- Supabase account (free tier works!)

## Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/rafidalhaque/ctf-scoreboard.git
cd ctf-scoreboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Setup Supabase

1. Go to [Supabase](https://supabase.com) and create a new project
2. Wait for the project to be ready (1-2 minutes)
3. Go to **SQL Editor** in the left sidebar
4. Click **New Query**
5. Copy the entire content of `schema.sql` from this repository
6. Paste it into the query editor and click **Run**
7. You should see "Success. No rows returned"

## Step 3: Get Your Credentials

### CTFd API Credentials

1. Log in to your CTFd instance as admin
2. Go to **Settings** → **Access Tokens**
3. Click **Generate**
4. Copy the token

### Supabase Credentials

1. In your Supabase project, go to **Settings** → **API**
2. Copy the **Project URL** (looks like `https://xxxxx.supabase.co`)
3. Copy the **anon public** key (starts with `eyJ...`)

## Step 4: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use any text editor
```

Fill in these required values:

```env
CTFD_API_URL=https://your-ctfd-instance.com/api/v1
CTFD_API_KEY=ctfd_your_token_here
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJ...your_key_here
```

Optional settings:

```env
CTFD_EVENT_NAME=My Awesome CTF 2024
REFRESH_INTERVAL=60
TOP_TEAMS_COUNT=10
```

## Step 5: Run the Application

```bash
python app.py
```

You should see:

```
INFO - Scheduler started with interval: 60 seconds
INFO - Starting Flask app on 0.0.0.0:5000
```

## Step 6: View Your Scoreboard

Open your browser and go to:

```
http://localhost:5000
```

You should see your CTFd scoreboard! 🎉

## Troubleshooting

### "Missing required environment variables"

Make sure you've filled in all required variables in `.env`:
- `CTFD_API_URL`
- `CTFD_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### "Error connecting to CTFd API"

- Verify your `CTFD_API_URL` includes `/api/v1`
- Check that your API key is valid
- Ensure your CTFd instance is accessible

### "Error connecting to Supabase"

- Verify your Supabase URL and key are correct
- Make sure you've run the `schema.sql` in Supabase
- Check that your Supabase project is active

### No data showing

- Wait for the first refresh cycle (60 seconds by default)
- Check the console logs for errors
- Verify there's actually data in your CTFd scoreboard

## Next Steps

- **Customize**: Edit `templates/index.html` to customize the look
- **Deploy**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options
- **Monitor**: Check `/health` endpoint for status
- **API**: Use `/api/scoreboard` for JSON data

## Common Customizations

### Change refresh interval

In `.env`:
```env
REFRESH_INTERVAL=30  # Update every 30 seconds
```

### Show more teams

In `.env`:
```env
TOP_TEAMS_COUNT=20  # Show top 20 teams
```

### Change port

In `.env`:
```env
FLASK_PORT=8080  # Run on port 8080
```

## Using Docker

If you prefer Docker:

```bash
# Build the image
docker build -t ctf-scoreboard .

# Run the container
docker run -d -p 5000:5000 --env-file .env ctf-scoreboard

# Or use docker-compose
docker-compose up -d
```

## Getting Help

- Check [README.md](README.md) for detailed documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guides
- Review application logs for error messages
- Check Supabase dashboard for database issues

## Validation

Run the test script to validate your setup:

```bash
python test_setup.py
```

All tests should pass! ✓

---

**Enjoy your CTFd Public Scoreboard!** 🏆
