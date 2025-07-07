# AI Link Scraper

An intelligent agent that monitors Slack channels for shared links, scrapes their content, generates summaries, and organizes them in a structured folder system.

## Features

- 🔗 **Slack Integration**: Automatically monitors specified Slack channels for links
- 🌐 **Web Scraping**: Intelligently extracts content from various website types
- 🤖 **AI Summarization**: Uses OpenAI's GPT models to generate concise summaries
- 📁 **Organized Storage**: Saves summaries with metadata in a structured format
- ⏰ **Batch Processing**: Processes multiple links efficiently
- 🔍 **Link Detection**: Identifies URLs in Slack messages with smart filtering

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_CHANNEL_ID=C1234567890

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Optional Configuration
OUTPUT_FOLDER=summaries
MAX_LINKS_PER_RUN=50
SUMMARY_MAX_LENGTH=500
```

### 3. Slack App Setup

1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app
3. Assign the following permissions to your app (if available):
    - `authorizations:read`
    - `connections:write`
    - `app_configurations:write`
4. Install the app to your workspace
5. Copy the Bot User OAuth Token to your `.env` file

### 4. Get Channel ID

1. Open Slack in browser
2. Navigate to your target channel
3. Copy the channel ID from the URL (e.g., `C1234567890`)

## Usage

### Basic Usage

```bash
python main.py
```

### Advanced Options

```bash
# Process specific date range
python main.py --start-date 2024-01-01 --end-date 2024-01-31

# Process specific number of messages
python main.py --limit 100

# Use custom output folder
python main.py --output-folder custom_summaries
```

## Project Structure

```
ai-link-scraper/
├── main.py                 # Main entry point
├── src/
│   ├── slack_client.py     # Slack API integration
│   ├── web_scraper.py      # Web content extraction
│   ├── summarizer.py       # AI summarization
│   └── utils.py           # Utility functions
├── config/
│   └── settings.py        # Configuration management
├── summaries/             # Generated summaries (created automatically)
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Configuration Options

- `SLACK_BOT_TOKEN`: Your Slack bot token
- `SLACK_CHANNEL_ID`: Target Slack channel ID
- `OPENAI_API_KEY`: OpenAI API key for summarization
- `OUTPUT_FOLDER`: Directory to save summaries (default: "summaries")
- `MAX_LINKS_PER_RUN`: Maximum links to process per execution
- `SUMMARY_MAX_LENGTH`: Maximum length of generated summaries

## Output Format

Summaries are saved as JSON files with the following structure:

```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "summary": "AI-generated summary of the content...",
  "timestamp": "2024-01-15T10:30:00Z",
  "slack_message_id": "1234567890.123456",
  "word_count": 1500,
  "tags": ["technology", "ai", "programming"]
}
```

## Troubleshooting

### Common Issues

1. **Slack API Rate Limits**: The tool respects rate limits automatically
2. **OpenAI API Errors**: Ensure your API key is valid and has sufficient credits
3. **Web Scraping Failures**: Some sites may block scraping; this is handled gracefully
4. **Permission Errors**: Ensure the Slack bot has access to the target channel

### Logs

Check the `logs/` directory for detailed execution logs and error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
