# Task Tracker Pro - Deployment Guide

## Prerequisites
- Git repository (push your code to GitHub)
- Choose a deployment platform

## Option 1: Deploy to Railway (Recommended)

Railway is free and easy to use:

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect the Dockerfile and deploy

3. **Set Environment Variables** (in Railway dashboard):
   ```
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://... (Railway provides this automatically if you add PostgreSQL)
   ```

4. **Add PostgreSQL Database**:
   - In Railway dashboard, click "New" → "Database" → "PostgreSQL"
   - Railway will automatically set DATABASE_URL

## Option 2: Deploy to Render

1. **Push to GitHub** (if not already done)

2. **Deploy to Render**:
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`

3. **Add PostgreSQL Database**:
   - In Render dashboard, create a new PostgreSQL database
   - Copy the DATABASE_URL to your web service environment variables

## Option 3: Deploy to Heroku

1. **Install Heroku CLI** and login:
   ```bash
   brew install heroku/brew/heroku
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   cd /path/to/your/project
   heroku create your-app-name
   ```

3. **Add PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key-here
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

## Environment Variables Needed

For production deployment, set these environment variables:

- `SECRET_KEY`: A secure random string
- `DATABASE_URL`: PostgreSQL connection string (usually provided by the platform)
- `FLASK_ENV`: Set to "production"

Optional:
- `MAIL_SERVER`: For email notifications
- `MAIL_USERNAME`: Email username
- `MAIL_PASSWORD`: Email password
- `REDIS_URL`: For real-time features

## Post-Deployment

After deployment:
1. Your app will be available at the provided URL
2. The database will be automatically initialized on first run
3. Create your first user account through the registration page

## Troubleshooting

- Check the logs in your platform's dashboard
- Ensure all environment variables are set
- Make sure the PORT environment variable is used (platforms provide this automatically)
