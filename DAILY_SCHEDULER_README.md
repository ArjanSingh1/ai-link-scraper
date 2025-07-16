# AI Link Scraper Daily Scheduler

## Overview

The Daily Scheduler automatically runs every 24 hours to:
1. **Scrape only yesterday's Slack messages** for shared links
2. **Process and summarize new links** using AI
3. **Add data to existing files** (incremental, not replacing)
4. **Maintain a growing master dataset** over time

## Key Features

- ✅ **Incremental Processing**: Only processes new data, never duplicates
- ✅ **Daily Automation**: Runs automatically every morning at 9:00 AM
- ✅ **Data Persistence**: Accumulates data in master files over time
- ✅ **Duplicate Prevention**: Filters out already processed links

## Quick Start

### 1. Install Dependencies
```bash
pip install schedule
```

### 2. Run Immediately (Test)
```bash
# Run a daily update right now
python daily_scheduler.py --run-now

# Or use the startup script
./start_daily_service.sh run-now
```

### 3. Check Status
```bash
python daily_scheduler.py --status
```


## Setup for Automatic Daily Runs

### GitHub Actions (Recommended)

You can automate daily scraping using GitHub Actions. This runs the scheduler every day in the cloud, with no need for local cron or a server.

#### 1. Add your secrets to GitHub:
Go to your repository > Settings > Secrets and variables > Actions > New repository secret, and add:

- `SLACK_BOT_TOKEN`
- `SLACK_CHANNEL_ID`
- `OPENAI_API_KEY`

#### 2. Workflow file:
The workflow is in `.github/workflows/daily-scrape.yml` and runs every day at 9:00 AM UTC.

#### 3. Monitor runs:
Go to the **Actions** tab in your GitHub repo to see logs and results for each daily run.

#### 4. Manual run:
You can also trigger the workflow manually from the Actions tab.

---

## File Structure

The daily scheduler creates and maintains these files:

```
ai-link-scraper/
├── master_links_data.csv          # Master CSV with all processed links
├── daily_summaries/               # Organized daily summaries
│   ├── 2025-01-15/               # Date-based folders
│   │   ├── summary_001_title.txt
│   │   └── summary_002_title.txt
│   └── 2025-01-16/
├── last_run.json                 # Status of last run
└── logs/
    ├── daily_scheduler.log        # Scheduler logs
    └── cron.log                   # Cron execution logs
```

## Data Processing Flow

1. **🕘 9:00 AM Daily**: Scheduler triggers
2. **📅 Date Calculation**: Identifies yesterday's date range
3. **📥 Slack Fetch**: Gets messages from yesterday only
4. **🔗 Link Extraction**: Finds all URLs in messages
5. **🔍 Deduplication**: Filters out already processed links
6. **🤖 AI Processing**: Scrapes content and generates summaries
7. **💾 Data Storage**: Appends new data to master CSV
8. **📁 Organization**: Saves summaries in date-based folders

## Configuration

### Environment Variables (.env)
```bash
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL_ID=C04FLMADLRM
OPENAI_API_KEY=sk-your-key
SUMMARY_MAX_LENGTH=500
```

### Scheduler Settings (daily_scheduler.py)
```python
# Run time (24-hour format)
schedule.every().day.at("09:00").do(self._daily_scrape_job)

# File locations
self.master_data_file = "master_links_data.csv"
self.master_summaries_dir = "daily_summaries"
```

## Monitoring & Troubleshooting

### Check Last Run Status
```bash
python daily_scheduler.py --status
```

### View Logs
```bash
# Scheduler logs
tail -f logs/daily_scheduler.log

# Cron logs (if using cron)
tail -f logs/cron.log
```

### Manual Testing
```bash
# Test with specific date
python src/update_all.py --date 2025-01-15

# Test Slack only
python src/update_all.py --slack-only

# Test B2B Vault only
python src/update_all.py --b2b-only --b2b-articles 5
```

### Common Issues

1. **No new links processed**: All links may already be in master file
2. **Slack API errors**: Check token and channel permissions
3. **Permission errors**: Ensure write access to data directories
4. **Cron not running**: Check `crontab -l` and system time

## Data Output

### Master CSV Columns
- `title`: Article/page title
- `url`: Original URL
- `domain`: Website domain
- `content_type`: Type of content detected
- `word_count`: Number of words in content
- `date_shared`: When shared in Slack
- `shared_by`: Slack user who shared
- `summary`: AI-generated summary
- `date_processed`: Date the scheduler processed it
- `processing_date`: Exact timestamp of processing

### Daily Summary Files
- Individual `.txt` files for each processed link
- Organized by date in `daily_summaries/YYYY-MM-DD/`
- Includes full summary, metadata, and original URL

## Integration with Existing System

The daily scheduler works alongside the existing AI Link Scraper:
- **Existing system**: On-demand processing, mentions, manual runs
- **Daily scheduler**: Automatic incremental processing
- **Shared data**: Both use the same master CSV file
- **No conflicts**: Deduplication prevents processing same links twice

## Advanced Usage

### Custom Date Processing
```python
from src.update_all import DailyDataUpdater
from datetime import datetime

updater = DailyDataUpdater()

# Process specific date
target_date = datetime(2025, 1, 15)
count = updater.update_slack_daily(target_date)
print(f"Processed {count} links")
```

### Batch Historical Processing
```bash
# Process multiple days (run manually)
for date in 2025-01-10 2025-01-11 2025-01-12; do
    python src/update_all.py --date $date
done
```

This setup ensures your AI Link Scraper continuously grows its knowledge base with fresh content every day, without manual intervention or duplicate processing.
