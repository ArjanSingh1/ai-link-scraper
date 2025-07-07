# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup Environment
```bash
# Clone or navigate to the project
cd ai-link-scraper

# Run setup (this creates virtual environment and installs dependencies)
python setup.py

# Verify setup
python test_setup.py
```

### Step 2: Configure API Keys
Edit the `.env` file with your credentials:

```env
# Get these from https://api.slack.com/apps
SLACK_BOT_TOKEN=xoxb-your-actual-token
SLACK_CHANNEL_ID=C1234567890

# Get this from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-actual-key
```

### Step 3: Run the Scraper
```bash
# Basic usage - scrape links from last 7 days
python main.py

# Scrape ALL historical links (no limits)
python main.py --max-links 99999 --limit 99999

# Send summaries back to Slack as messages (shorter format)
python main.py --send-to-slack

# Upload summary files to Slack
python main.py --upload-to-slack

# Send a digest of recent summaries to Slack
python main.py --share-digest

# Share ALL summaries in one organized file
python main.py --share-all-summaries

# Complete workflow: scrape, summarize, and share everything
python main.py --send-to-slack --share-all-summaries --verbose

# NEW: Check for mentions and respond immediately
python main.py --check-mentions              # Check configured channel only
python main.py --check-all-channels         # Check ALL accessible channels
```

## 🤖 Enhanced Mention Feature

Your bot now responds to mentions **across ALL channels** it has access to!

### How to Use:
1. **Share a link with mention**: `@ailinkscraper https://example.com/article` (in any channel)
2. **Get instant summary**: Bot will immediately scrape and summarize the link
3. **Automatic responses**: Every 15 minutes, 7 AM - 10 PM EST (extended hours)

### Mention Commands:
- `@ailinkscraper` + any link = Instant summary (works in any channel)
- `@ailinkscraper` alone = Help message with usage instructions

### Enhanced Scheduling:
- **Weekly scraping**: Every Monday at 1:05 PM EST (6:05 PM UTC)
- **Mention checking**: Every 15 minutes, 7 AM - 10 PM EST (across ALL channels)
- **Manual trigger**: Available anytime through GitHub Actions

### Required Bot Permissions:
Your Slack bot needs these scopes for full functionality:
- `channels:history` - Read messages from public channels
- `groups:history` - Read messages from private channels  
- `channels:read` - Get channel information
- `groups:read` - Get private channel information
- `chat:write` - Send messages
- `files:write` - Upload files
- `links:read` - Handle links

## 📋 Slack Setup Checklist

1. **Create Slack App**
   - Go to https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Name your app (e.g., "Link Scraper Bot")
   - Select your workspace

2. **Configure Bot Permissions**
   - Go to "OAuth & Permissions"
   - Add Bot Token Scopes:
     - `channels:history` (to read messages)
     - `channels:read` (to access channel info)
     - `chat:write` (to send summary messages)
     - `files:write` (to upload summary files)

3. **Install App**
   - Click "Install to Workspace"
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)

4. **Get Channel ID**
   - Open Slack in browser
   - Navigate to your target channel
   - Copy the channel ID from URL: `/channels/C1234567890`

## 📊 Understanding Output

The scraper creates JSON files in the `summaries/` folder with this structure:

```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "summary": "AI-generated summary...",
  "tags": ["ai", "technology", "programming"],
  "timestamp": "2024-01-15T10:30:00Z",
  "slack_message_id": "1234567890.123456",
  "word_count": 1500
}
```

### 📂 Viewing Your Summaries

```bash
# Open summaries folder in Finder (Mac)
open summaries/

# List all summary files
ls summaries/

# View a specific summary (formatted with jq)
cat summaries/"filename.json" | jq .

# View all summaries
find summaries/ -name "*.json" -exec echo "=== {} ===" \; -exec cat {} \; -exec echo "" \;
```

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | Run `python setup.py` again |
| Slack connection fails | Check bot token and permissions |
| OpenAI errors | Verify API key and billing |
| No links found | Check channel ID and date range |
| Web scraping fails | Some sites block scrapers (normal) |

## 🔧 Advanced Usage

```bash
# Verbose logging
python main.py --verbose

# Scrape ALL historical links (no limits)
python main.py --max-links 99999 --limit 99999 --verbose

# Send short summaries to Slack as messages
python main.py --send-to-slack --verbose

# Upload summary files to Slack
python main.py --upload-to-slack --verbose

# Share a digest of recent summaries
python main.py --share-digest

# Share complete organized summary collection
python main.py --share-all-summaries

# Complete workflow: scrape, summarize, and share everything
python main.py --send-to-slack --share-all-summaries --verbose

# Process only recent messages
python main.py --limit 10

# Custom date range with sharing
python main.py --start-date 2024-01-01 --end-date 2024-01-15 --send-to-slack --share-digest

# Combine all options
python main.py --start-date 2024-01-01 --limit 50 --send-to-slack --share-all-summaries --verbose
```

## 📁 Project Structure

```
ai-link-scraper/
├── main.py              # Main script
├── setup.py             # Setup and installation
├── test_setup.py        # Verify installation
├── examples.py          # Component examples
├── requirements.txt     # Dependencies
├── .env                 # Your API keys (create this)
├── src/                 # Core modules
│   ├── slack_client.py  # Slack integration
│   ├── web_scraper.py   # Web content extraction
│   ├── summarizer.py    # AI summarization
│   └── utils.py         # Helper functions
├── config/              # Configuration
│   └── settings.py      # Settings management
├── summaries/           # Generated summaries (auto-created)
└── logs/                # Application logs (auto-created)
```

## 🎯 Next Steps

1. **Automate with Cron**: Schedule regular runs
2. **Database Storage**: Store summaries in database instead of files
3. **Web Dashboard**: Create a web interface to browse summaries
4. **Slack Bot**: Send summaries back to Slack
5. **Email Digest**: Send weekly summary emails

Happy scraping! 🕷️✨
