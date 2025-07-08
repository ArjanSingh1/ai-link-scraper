# Google Drive Integration Setup

This guide explains how to set up Google Drive integration for the AI Link Scraper.

## 🚀 Quick Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Name it something like "AI Link Scraper"

### Step 2: Enable Google Drive API

1. In your Google Cloud project, go to **APIs & Services** > **Library**
2. Search for "Google Drive API"
3. Click on it and press **Enable**

### Step 3: Create Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **+ Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External** (unless you have Google Workspace)
   - App name: "AI Link Scraper"
   - User support email: Your email
   - Developer contact: Your email
4. Application type: **Desktop application**
5. Name: "AI Link Scraper Desktop"
6. Click **Create**

### Step 4: Download Credentials

1. After creating, click the **Download** button (⬇️) next to your OAuth client
2. Save the downloaded file as `credentials.json` in the `config/` folder of your project
3. The file path should be: `config/credentials.json`

### Step 5: Test the Setup

```bash
# Test Google Drive integration
python main.py --scrape-to-drive --start-date 2024-01-01 --limit 5

# Or scrape recent links
python main.py --scrape-to-drive --verbose
```

## 🔧 Configuration Options

### Environment Variables

Add to your `.env` file (optional):

```bash
# Optional: Specify a default Google Drive folder ID
GOOGLE_DRIVE_FOLDER_ID=your-folder-id-here
```

### Command Line Usage

```bash
# Basic usage - scrape all recent links to Google Drive
python main.py --scrape-to-drive

# Scrape with custom folder name
python main.py --scrape-to-drive --drive-folder-name "Weekly Links"

# Scrape specific date range
python main.py --scrape-to-drive --start-date 2024-01-01 --end-date 2024-01-31

# Limit number of links
python main.py --scrape-to-drive --max-links 20

# Verbose logging
python main.py --scrape-to-drive --verbose
```

## 📁 Output Files

The scraper will create three files in Google Drive:

1. **CSV file** - Spreadsheet format for easy viewing/filtering
2. **JSON file** - Machine-readable format with all data
3. **HTML file** - Beautiful web report with clickable links

### CSV Columns:
- `url` - The original link
- `title` - Page title
- `tags` - Comma-separated tags (tech, business, news, etc.)
- `word_count` - Number of words on the page
- `domain` - Website domain
- `content_preview` - First 200 characters of content
- `slack_user` - Who shared the link in Slack
- `slack_timestamp` - When it was shared
- `scraped_at` - When we processed it

## 🎯 Features

### Automatic Tagging

The system automatically adds tags based on:
- **Content keywords**: tech, business, news
- **Domain recognition**: github, medium, youtube, twitter
- **Content length**: short, article, long-read

### Public Sharing

All uploaded files are automatically made publicly viewable (anyone with the link can access).

### Folder Organization

Each run creates a timestamped folder like:
- `ai-link-scraper_2024-07-07_14-30/`
  - `scraped_links_20240707_1430.csv`
  - `scraped_links_20240707_1430.json` 
  - `scraped_links_20240707_1430.html`

## 🔒 Authentication

### First Run

On your first run, the system will:
1. Open your browser automatically
2. Ask you to sign in to Google
3. Request permission to access Google Drive
4. Save credentials for future use

The credentials are saved in `config/token.json` and will be reused automatically.

### Troubleshooting

**"File not found: config/credentials.json"**
- Make sure you downloaded the OAuth credentials file
- Place it in the `config/` folder
- Rename it to exactly `credentials.json`

**"Authentication failed"**
- Delete `config/token.json` and try again
- This forces a fresh authentication

**"Quota exceeded"**
- You've hit Google's API limits
- Wait a few minutes and try again
- Consider reducing `--max-links`

## 🔗 Integration with Existing Workflows

### With Daemon Mode

```bash
# Run daemon with Google Drive export
python daemon.py --export-to-drive  # (coming soon)
```

### With Slack Bot

The bot can automatically export links to Google Drive when mentioned:
- `@ailinkscraper export recent links` (coming soon)

### Scheduled Exports

Add to your weekly GitHub Actions workflow:
```yaml
- name: Export to Google Drive
  run: python main.py --scrape-to-drive --start-date 7-days-ago
```

## 📊 Example Output

After running `--scrape-to-drive`, you'll see:

```
=== GOOGLE DRIVE EXPORT COMPLETE ===
Total links processed: 15
📁 Google Drive folder: https://drive.google.com/drive/folders/1ABC...
📊 CSV file: https://drive.google.com/file/d/1DEF.../view
🌐 HTML report: https://drive.google.com/file/d/1GHI.../view
```

The CSV will look like:
| title | url | tags | domain | word_count | slack_user |
|-------|-----|------|--------|------------|------------|
| "How to Build APIs" | https://example.com/api | tech, article | example.com | 1250 | john.doe |
| "Startup Funding Guide" | https://business.com/funding | business, long-read | business.com | 3200 | jane.smith |

Perfect for sharing with your team or importing into other tools! 🎉
