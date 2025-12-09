# Deployment Guide

This guide provides detailed instructions for deploying the CTFd Public Scoreboard to various platforms.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Heroku Deployment](#heroku-deployment)
3. [Railway Deployment](#railway-deployment)
4. [Traditional VPS Deployment](#traditional-vps-deployment)
5. [Environment Variables](#environment-variables)

## Docker Deployment

### Prerequisites
- Docker installed on your system
- Docker Compose (optional, for easier management)

### Steps

1. **Create Dockerfile**

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production

# Run the application
CMD ["python", "app.py"]
```

2. **Build the Docker image**

```bash
docker build -t ctf-scoreboard .
```

3. **Run the container**

```bash
docker run -d \
  -p 5000:5000 \
  --env-file .env \
  --name ctf-scoreboard \
  ctf-scoreboard
```

4. **Using Docker Compose** (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  scoreboard:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
```

Run with:

```bash
docker-compose up -d
```

### Docker Best Practices

- Use multi-stage builds to reduce image size
- Don't include `.env` file in the image (use environment variables or secrets)
- Use health checks in Docker Compose
- Set appropriate resource limits

## Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI installed

### Steps

1. **Create a Procfile**

Create `Procfile` in the project root:

```
web: python app.py
```

2. **Create runtime.txt**

Specify Python version in `runtime.txt`:

```
python-3.11.7
```

3. **Initialize Git repository** (if not already)

```bash
git init
git add .
git commit -m "Initial commit"
```

4. **Create Heroku app**

```bash
heroku create your-ctf-scoreboard
```

5. **Set environment variables**

```bash
heroku config:set CTFD_EVENT_NAME="Your CTF Event"
heroku config:set CTFD_API_URL="https://your-ctfd.com/api/v1"
heroku config:set CTFD_API_KEY="your_api_key"
heroku config:set SUPABASE_URL="https://your-project.supabase.co"
heroku config:set SUPABASE_KEY="your_supabase_key"
heroku config:set FLASK_SECRET_KEY="$(openssl rand -hex 32)"
```

6. **Deploy**

```bash
git push heroku main
```

7. **Scale the app**

```bash
heroku ps:scale web=1
```

8. **Open the app**

```bash
heroku open
```

## Railway Deployment

### Prerequisites
- Railway account
- Railway CLI (optional)

### Steps

1. **Via Railway Dashboard**

   - Go to [Railway](https://railway.app/)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository
   - Railway will auto-detect the Python app

2. **Set Environment Variables**

   In the Railway dashboard:
   - Go to your project
   - Click on "Variables"
   - Add all required environment variables from `.env.example`

3. **Deploy**

   Railway will automatically deploy on every git push to the main branch.

4. **Custom Domain** (Optional)

   - Go to "Settings" → "Domains"
   - Add your custom domain
   - Configure DNS records as instructed

### Via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Set environment variables
railway variables set CTFD_API_URL=https://your-ctfd.com/api/v1
# ... set other variables
```

## Traditional VPS Deployment

### Prerequisites
- VPS with Ubuntu 20.04+ or similar
- SSH access
- Domain name (optional)

### Steps

1. **Update system**

```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install Python and dependencies**

```bash
sudo apt install python3 python3-pip python3-venv nginx -y
```

3. **Create application user**

```bash
sudo useradd -m -s /bin/bash ctfscoreboard
sudo su - ctfscoreboard
```

4. **Clone repository**

```bash
git clone https://github.com/rafidalhaque/ctf-scoreboard.git
cd ctf-scoreboard
```

5. **Setup virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. **Configure environment**

```bash
cp .env.example .env
nano .env  # Edit with your values
```

7. **Create systemd service**

Exit from the application user and create `/etc/systemd/system/ctf-scoreboard.service`:

```ini
[Unit]
Description=CTF Scoreboard
After=network.target

[Service]
User=ctfscoreboard
Group=ctfscoreboard
WorkingDirectory=/home/ctfscoreboard/ctf-scoreboard
Environment="PATH=/home/ctfscoreboard/ctf-scoreboard/venv/bin"
ExecStart=/home/ctfscoreboard/ctf-scoreboard/venv/bin/python app.py

[Install]
WantedBy=multi-user.target
```

8. **Start and enable service**

```bash
sudo systemctl daemon-reload
sudo systemctl start ctf-scoreboard
sudo systemctl enable ctf-scoreboard
sudo systemctl status ctf-scoreboard
```

9. **Configure Nginx reverse proxy**

Create `/etc/nginx/sites-available/ctf-scoreboard`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

10. **Enable site and restart Nginx**

```bash
sudo ln -s /etc/nginx/sites-available/ctf-scoreboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

11. **Setup SSL with Let's Encrypt** (Optional)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Environment Variables

All environment variables should be set according to your environment. Here's a complete list:

### Required Variables

```bash
# CTFd Configuration
CTFD_API_URL=https://your-ctfd-instance.com/api/v1
CTFD_API_KEY=your_ctfd_api_token

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### Optional Variables

```bash
# Event Configuration
CTFD_EVENT_NAME="My CTF Event"

# Timing
REFRESH_INTERVAL=60  # seconds

# Flask Configuration
FLASK_SECRET_KEY=your-random-secret-key
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Display
TOP_TEAMS_COUNT=10
```

## Monitoring and Maintenance

### Logs

**Docker:**
```bash
docker logs -f ctf-scoreboard
```

**Heroku:**
```bash
heroku logs --tail
```

**VPS (systemd):**
```bash
sudo journalctl -u ctf-scoreboard -f
```

### Health Check

The application provides a health check endpoint:

```bash
curl http://your-domain.com/health
```

### Updating the Application

**Docker:**
```bash
docker-compose down
git pull
docker-compose up -d --build
```

**Heroku:**
```bash
git pull
git push heroku main
```

**VPS:**
```bash
sudo su - ctfscoreboard
cd ctf-scoreboard
source venv/bin/activate
git pull
pip install -r requirements.txt
exit
sudo systemctl restart ctf-scoreboard
```

## Troubleshooting

### Common Issues

1. **Application won't start**
   - Check environment variables are set correctly
   - Verify Supabase credentials
   - Check application logs

2. **Can't connect to CTFd**
   - Verify API URL is correct
   - Check API key is valid
   - Ensure CTFd instance is accessible

3. **Database errors**
   - Verify Supabase connection
   - Ensure schema.sql has been run
   - Check RLS policies

4. **Port already in use**
   - Change FLASK_PORT in environment variables
   - Check for other processes using the port

## Security Considerations

1. **Never commit .env file** - It contains sensitive credentials
2. **Use strong secret keys** - Generate with `openssl rand -hex 32`
3. **Enable HTTPS** - Use Let's Encrypt or similar
4. **Keep dependencies updated** - Regularly run `pip install -U -r requirements.txt`
5. **Monitor logs** - Watch for suspicious activity
6. **Rate limiting** - Consider adding rate limiting for public endpoints
7. **Firewall** - Only expose necessary ports

## Performance Optimization

1. **Use a CDN** - For static assets
2. **Enable caching** - Cache database queries
3. **Scale horizontally** - Use multiple instances with load balancer
4. **Database indexes** - Already included in schema.sql
5. **Optimize refresh interval** - Balance between freshness and API load

## Support

For issues or questions:
- Check the [README.md](README.md) for basic setup
- Review application logs
- Check Supabase dashboard for database issues
- Verify CTFd API is accessible
