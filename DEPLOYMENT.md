# Deployment Options for AI Link Scraper

## 1. Vercel (Recommended)

### Quick Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/ai-link-scraper)

### Manual Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Add environment variables in Vercel dashboard:
# - SLACK_BOT_TOKEN
# - OPENAI_API_KEY
# - SLACK_CHANNEL_ID
```

## 2. Railway

### Quick Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/your-username/ai-link-scraper)

### Manual Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway link
railway up

# Add environment variables in Railway dashboard
```

## 3. Render

### Quick Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/your-username/ai-link-scraper)

### Manual Deployment
1. Connect your GitHub repo to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn website.app:app`
4. Add environment variables

## 4. Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy

# Set environment variables
fly secrets set SLACK_BOT_TOKEN=your-token
fly secrets set OPENAI_API_KEY=your-key
```

## Environment Variables Required

- `SLACK_BOT_TOKEN`: Your Slack bot token
- `OPENAI_API_KEY`: Your OpenAI API key  
- `SLACK_CHANNEL_ID`: Your Slack channel ID
- `OUTPUT_FOLDER`: summaries (default)
- `MAX_LINKS_PER_RUN`: 99999 (default)
