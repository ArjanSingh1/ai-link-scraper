#!/bin/bash

echo "🚀 AI Link Scraper - GitHub Setup"
echo "=================================="

# Check if repository URL is provided
if [ "$1" = "" ]; then
    echo "❌ Please provide your GitHub repository URL"
    echo "Usage: ./setup_github.sh https://github.com/YOUR_USERNAME/ai-link-scraper.git"
    echo ""
    echo "Steps to create repository:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: ai-link-scraper"
    echo "3. Make it public or private"
    echo "4. Don't initialize with README (we already have one)"
    echo "5. Copy the repository URL"
    exit 1
fi

REPO_URL=$1

echo "📂 Setting up repository: $REPO_URL"

# Add remote origin
git remote add origin $REPO_URL

# Push to GitHub
echo "⬆️ Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Repository setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Go to your repository on GitHub"
echo "2. Go to Settings → Secrets and variables → Actions"
echo "3. Add these Repository Secrets:"
echo "   - SLACK_BOT_TOKEN (your bot token)"
echo "   - SLACK_CHANNEL_ID (your channel ID)"
echo "   - OPENAI_API_KEY (your OpenAI key)"
echo ""
echo "4. Test the setup:"
echo "   - Go to Actions tab"
echo "   - Click 'Test AI Link Scraper'"
echo "   - Click 'Run workflow'"
echo ""
echo "5. The weekly scraper will run automatically every Monday at 9 AM UTC!"
echo ""
echo "🎉 Happy scraping!"
