
# AI Link Scraper & B2B Vault Scraper (with Voting System)


## AI Link Scraper

An intelligent agent that monitors Slack channels for shared links, scrapes their content, generates summaries, and organizes them in a structured folder system.

### Features
- 🔗 **Slack Integration**: Monitors Slack channels for links
- 🌐 **Web Scraping**: Extracts content from various websites
- 🤖 **AI Summarization**: Uses OpenAI's GPT models
- 📁 **Organized Storage**: Saves summaries with metadata
- ⏰ **Batch Processing**: Efficiently processes multiple links
- 🔍 **Link Detection**: Smart URL filtering

### Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.env` in the project root:
   ```env
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_CHANNEL_ID=C1234567890
   OPENAI_API_KEY=sk-your-openai-api-key
   OUTPUT_FOLDER=summaries
   MAX_LINKS_PER_RUN=50
   SUMMARY_MAX_LENGTH=500
   ```
3. [Slack App Setup](https://api.slack.com/apps): Create an app, assign permissions, install, and copy the Bot User OAuth Token to `.env`.
4. Get your channel ID from the Slack URL.

### Usage
```bash
python main.py
# or with options:
python main.py --start-date 2024-01-01 --end-date 2024-01-31 --limit 100 --output-folder custom_summaries
```

### Output Format
Summaries are saved as JSON files:
```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "summary": "AI-generated summary...",
  "timestamp": "2024-01-15T10:30:00Z",
  "slack_message_id": "1234567890.123456",
  "word_count": 1500,
  "tags": ["technology", "ai", "programming"]
}
```

---

## B2B Vault Scraper

A Python web scraper to extract company and contact info from B2B websites.

### Features
- Extract company names, descriptions, contact info
- Find emails, phone numbers, social media links
- Export to CSV/JSON
- Configurable delays, logging, and ethical scraping

### Usage
```python
from B2Bscraper import B2BVaultScraper
scraper = B2BVaultScraper(delay=1.0)
data = scraper.scrape_url("https://example.com")
urls = ["https://company1.com", "https://company2.com"]
results = scraper.scrape_urls(urls)
scraper.save_to_csv(results)
scraper.save_to_json(results)
```

#### Advanced Usage
```python
scraper = B2BVaultScraper(delay=2.0, output_dir="my_scraped_data")
for company in results:
    print(f"Company: {company['company_name']}")
    print(f"Email: {company['email']}")
    print(f"Phone: {company['phone']}")
```

#### Configuration
Edit `config.py` to customize delays, selectors, output, etc.

#### Output
- `scraped_companies.csv` / `scraped_companies.json`
- `scraper.log`, `last_fetched_page.html`

#### Legal/Ethical
Respect robots.txt, use delays, comply with terms and laws.

---

## 🗳️ B2B Vault Voting System

### Features
- Upvote/downvote articles
- Real-time scoring and feedback
- Persistent votes (JSON backend)
- User tracking (simple ID)
- Interactive website UI

### Usage
1. Generate website with voting:
   ```bash
   cd b2bvault-repo
   python3 B2Bscraper.py --preview --limit 20
   ```
2. View the website:
   ```bash
   cd scraped_data/website
   python3 start_server.py
   ```
3. Vote on articles via the UI

#### Example (Python)
```python
from voting_system import VotingSystem
voting = VotingSystem("votes.json")
result = voting.vote("https://article.com", "upvote", "user123")
votes = voting.get_votes("https://article.com")
top = voting.get_top_articles(limit=5)
```

#### Vote Data Structure
```json
{
  "article_url": {
    "upvotes": 5,
    "downvotes": 2,
    "voters": {"user_123": "upvote"},
    "created_at": "2025-07-16T10:30:00",
    "last_updated": "2025-07-16T11:45:00"
  }
}
```

#### Architecture
- `voting_system.py`: Core logic
- Website: Interactive UI
- `votes.json`: Persistent storage

#### Future Enhancements
- DB integration, user auth, analytics, comments, export

---

## Project Structure (Combined)

```
ai-link-scraper/
├── src/                  # Core modules (Slack, scraping, summarization, utils)
├── b2bvault-repo/        # B2B Vault scraper and voting system
├── scraped_data/         # Output data
├── requirements.txt      # All dependencies (consolidated)
├── .env                  # Environment variables
├── .github/              # GitHub Actions workflows
└── README.md             # This file
```

---

## License

MIT License - see LICENSE file for details.
