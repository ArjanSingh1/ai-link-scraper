# B2B Sales Intelligence Platform 🚀

A comprehensive sales intelligence platform that combines **AI Link Scraper** and **B2B Vault** functionality into one unified web-based dashboard.

## 🌟 Features

### AI Links Hub
- **Smart Link Scraping**: Automatically scrape and classify links from Slack channels
- **Content Analysis**: AI-powered content categorization and summarization
- **Export Capabilities**: CSV, HTML, and PDF export options
- **Google Drive Integration**: Automatic backup and sharing
- **Real-time Dashboard**: Live statistics and insights

### B2B Vault Intelligence
- **Article Scraping**: Extract the latest B2B sales and marketing content
- **Category Filtering**: Browse by Sales, Marketing, AI, ABM & GTM, and more
- **Smart Search**: Find relevant articles with advanced search functionality
- **Progress Tracking**: Real-time scraping progress and status updates
- **Demo Mode**: Pre-loaded sample data for immediate testing

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)
- Flask and required dependencies

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd ai-link-scraper
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install flask flask-cors pandas
   ```

4. **Start the platform**:
   ```bash
   python website/app.py
   ```

5. **Access the dashboard**:
   Open your browser to `http://localhost:5001`

## 🎯 Using the Platform

### AI Links Hub Tab
- **View Links**: Browse all scraped links with filtering and search
- **Run Scraper**: Trigger new scraping sessions with date ranges
- **Export Data**: Download your data in various formats
- **Statistics**: View real-time analytics and insights

### B2B Vault Intelligence Tab
- **Browse Articles**: Explore curated B2B sales and marketing content
- **Category Filtering**: Filter by specific topics (Sales, Marketing, AI, etc.)
- **Search**: Find articles using keywords and phrases
- **Scrape Fresh Content**: Start new scraping sessions for the latest articles
- **Progress Tracking**: Monitor scraping progress in real-time

## 🛠️ API Endpoints

### AI Links API
- `GET /api/links` - Get all scraped links
- `GET /api/stats` - Get link statistics
- `POST /api/scrape` - Start new scraping session
- `GET /api/search` - Search links

### B2B Vault API
- `GET /api/b2b-articles` - Get B2B Vault articles
- `GET /api/b2b-stats` - Get B2B Vault statistics
- `POST /api/b2b-scrape` - Start B2B Vault scraping
- `GET /api/b2b-scrape-status` - Check scraping progress
- `GET /api/b2b-categories` - Get available categories

## 📊 Data Management

### Database
The platform uses SQLite for data storage with two main tables:
- `ai_links` - Stores scraped links and metadata
- `b2b_articles` - Stores B2B Vault articles and summaries

### Data Export
- **JSON Export**: Full data export with metadata
- **CSV Export**: Structured data for analysis
- **PDF Reports**: Formatted reports for sharing

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///sales_intelligence.db
```

### B2B Vault Settings
The platform includes a demo B2B Vault integration with sample data. To connect to the real B2B Vault:

1. Install B2B Vault dependencies:
   ```bash
   pip install playwright weasyprint
   ```

2. Update the B2B Vault integration in `src/b2b_vault_integration.py`

## 🚦 Development

### Project Structure
```
ai-link-scraper/
├── website/
│   ├── app.py              # Flask backend
│   ├── index.html          # Frontend UI
│   └── sales_intelligence.db # SQLite database
├── src/
│   ├── web_scraper.py      # AI Link Scraper
│   └── b2b_vault_integration.py # B2B Vault integration
├── b2bvault-repo/          # B2B Vault repository
└── scraped_links/          # Scraped data storage
```

### Adding New Features
1. **Backend**: Add new routes in `website/app.py`
2. **Frontend**: Update `website/index.html` with new UI components
3. **Database**: Modify database schema in `SalesIntelligenceDB`

## 🔄 Integration Status

### ✅ Completed Features
- [x] Unified web dashboard with tabbed interface
- [x] AI Link Scraper integration
- [x] B2B Vault demo integration
- [x] SQLite database for data persistence
- [x] REST API endpoints
- [x] Real-time scraping progress tracking
- [x] Search and filtering functionality
- [x] Export capabilities

### 🚧 Next Steps
- [ ] Connect to live B2B Vault API
- [ ] Add user authentication
- [ ] Implement advanced analytics
- [ ] Add report scheduling
- [ ] Create mobile-responsive design
- [ ] Add data visualization charts

## 📱 Usage Examples

### Starting a B2B Vault Scraping Session
```javascript
// Frontend JavaScript
function startB2BScraping() {
    fetch('/api/b2b-scrape', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            tags: ['Sales', 'Marketing'],
            max_articles: 50
        })
    })
    .then(response => response.json())
    .then(data => console.log(data));
}
```

### Searching Articles
```javascript
// Search B2B Vault articles
function searchB2BArticles() {
    const query = document.getElementById('b2b-search').value;
    fetch(`/api/b2b-articles?search=${query}`)
        .then(response => response.json())
        .then(data => displayResults(data.articles));
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License.

## 🆘 Support

For questions or issues:
1. Check the logs in the terminal
2. Review the Flask debug output
3. Test API endpoints directly
4. Check database connections

## 🎉 Acknowledgments

- **AI Link Scraper**: Original Slack integration and content analysis
- **B2B Vault**: Sales and marketing content curation
- **Flask**: Web framework for the backend
- **SQLite**: Database for data persistence

---

**Happy Selling! 🚀**
