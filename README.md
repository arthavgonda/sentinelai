# 🔍 Automated OSINT & Threat Actor Profiling System

A comprehensive, high-performance Open Source Intelligence (OSINT) platform designed for rapid data collection, analysis, and threat actor profiling. This system aggregates data from 12+ APIs, performs intelligent correlation, and generates detailed confidence reports with visual analytics.

## 🎯 Project Overview

This system is designed to perform comprehensive intelligence gathering and threat actor profiling by:

1. **Aggregating Data**: Collects information from 12+ APIs including social media, news sources, search engines, and threat intelligence platforms
2. **Deep Analysis**: Analyzes blogs, articles, Google search results, and news articles to extract comprehensive information
3. **Intelligent Correlation**: Correlates data across multiple sources to verify identity and detect inconsistencies
4. **Confidence Scoring**: Generates accurate confidence scores (65-95%) based on multiple verification sources
5. **Threat Assessment**: Automatically identifies threat indicators and assesses risk levels
6. **Visual Analytics**: Provides beautiful, intuitive visualizations of all collected data

### Key Use Cases
- **Threat Actor Profiling**: Identify and profile known criminals, terrorists, and threat actors
- **Identity Verification**: Verify identities across multiple platforms
- **OSINT Investigations**: Comprehensive open-source intelligence gathering
- **Risk Assessment**: Automated threat indicator detection and risk scoring

## 🚀 Features

### Core Capabilities
- **Multi-Source Intelligence Gathering**: Integrates with Twitter, Instagram, GitHub, Reddit, News APIs, Google Search, Hunter.io, VirusTotal, Etherscan, Telegram, and more
- **Real-Time Data Collection**: Parallel API calls with intelligent timeout management (15-30 seconds for complete data collection)
- **Google Search Integration**: Extracts AI summaries, Knowledge Panels, and entity information
- **Blog & Article Analysis**: Web scraping for detailed blog and article content analysis
- **Image Analysis**: Google Vision API integration for face detection, labeling, and image matching
- **Threat Intelligence**: Automated threat indicator detection and risk assessment
- **Confidence Scoring**: Comprehensive analysis engine that generates confidence scores based on multiple verification sources

### Advanced Features
- **Circular Progress Bar**: Real-time progress tracking with time estimates
- **Profile Image Display**: Prominent display of extracted photos with thumbnail gallery
- **Confidence Reports**: Detailed analysis with risk assessment, data quality metrics, and recommendations
- **WebSocket Updates**: Real-time progress updates and data streaming
- **Intelligent Caching**: Multi-tier caching strategy for optimal performance
- **Correlation Engine**: Cross-platform data correlation and verification

## 🎯 How It Works

### Search Flow

1. **Input**: User provides a name, email, username, or phone number
2. **Query Type Detection**: System automatically detects or user selects query type
3. **Parallel API Calls**: System queries all APIs simultaneously for maximum speed
4. **Google Search**: Performs Google search to extract AI summaries and Knowledge Panels
5. **Blog/Article Scraping**: Searches and analyzes blogs and articles
6. **News Analysis**: Analyzes news articles from multiple sources
7. **Image Extraction**: Extracts and analyzes images from all sources
8. **Correlation**: Correlates data across all sources
9. **Analysis**: Performs comprehensive analysis and generates confidence score
10. **Report Generation**: Creates detailed confidence report with findings

### Confidence Score Calculation

The system calculates confidence scores using a weighted approach:

- **Google AI Summary (35%)**: If Google provides an AI summary, this heavily influences the score
- **Blog/Article Analysis (15%)**: Analyzes content quality, relevance, and verification matches
- **News Analysis (10%)**: Analyzes articles from multiple news sources
- **Data Coverage (12-20%)**: Percentage of APIs returning data
- **Consistency (12-15%)**: Cross-platform data consistency
- **Verification (12-15%)**: Multi-source verification
- **Data Quality (10%)**: Completeness, accuracy, and relevance

**Additional Boosts**:
- Multiple verification sources: +3-5%
- Detailed descriptions: +10%
- High content richness: +10%
- Knowledge Panel: +5%
- Recent news articles: +10%

**Minimum Scores**:
- With Google AI Summary: Minimum 65%
- Without AI Summary: Based on other factors

## 📊 System Architecture

### Backend (FastAPI)
```
backend/
├── main.py                 # FastAPI application, WebSocket handlers
├── config.py              # Configuration and API keys
├── database.py            # SQLAlchemy models and database setup
├── cache.py               # Redis caching manager
├── services/
│   ├── orchestrator.py    # API orchestration and parallel execution
│   ├── analysis_engine.py # Confidence scoring and risk assessment
│   ├── correlation.py     # Data correlation engine
│   ├── google_search.py   # Google search and AI summary extraction
│   ├── google_vision.py   # Google Vision API integration
│   ├── web_scraper.py     # Blog and article scraping
│   └── image_matcher.py   # Image matching and face recognition
├── api_clients/           # API client implementations
│   ├── twitter.py
│   ├── instagram.py
│   ├── instagram_scraper.py
│   ├── github.py
│   ├── reddit.py
│   ├── newsapi.py
│   ├── google_news.py
│   └── ...
└── utils/
    └── validators.py      # Input validation and normalization
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── components/
│   │   ├── ProfileView.jsx          # Main profile display
│   │   ├── ProfileImage.jsx         # Image display component
│   │   ├── ConfidenceReport.jsx     # Confidence report card
│   │   ├── CircularProgress.jsx     # Progress indicator
│   │   ├── APIResults.jsx           # API results display
│   │   └── results/                 # Result components for each API
│   ├── hooks/
│   │   └── useWebSocket.js          # WebSocket hook
│   └── App.jsx
```

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- Node.js 16+
- Redis (optional, for caching)
- PostgreSQL (optional, SQLite used by default)
- Google Cloud Vision API credentials (optional, for image analysis)

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Dehradun
```

2. **Create virtual environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API keys**
   - Copy `api_info` template and add your API keys
   - Add Google Vision API service account JSON to root directory as `service-account.json`

5. **Initialize database**
```bash
# Database will be created automatically on first run
# Using SQLite by default (osint.db)
```

6. **Start backend server**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start development server**
```bash
npm run dev
```

### Using Start Script

```bash
# Make script executable
chmod +x start.sh

# Run the script
./start.sh
```

This will:
- Start Docker services (PostgreSQL, Redis) if available
- Install backend and frontend dependencies
- Start both servers

## 📖 Usage

### Basic Search

1. **Open the application** in your browser (default: http://localhost:3000)

2. **Enter a query**:
   - **Name**: Full name (e.g., "John Doe", "Saif al-Adel")
   - **Email**: Email address
   - **Username**: Social media username
   - **Phone**: Phone number with country code

3. **Select query type** or use auto-detect

4. **View results**:
   - Profile image (if available)
   - Confidence report with scores
   - API results from all sources
   - Correlation analysis
   - Image matches

### Query Types

- **Name**: Searches across multiple platforms, news articles, blogs, and Google
- **Email**: Hunter.io email finder, domain analysis
- **Username**: Twitter, Instagram, GitHub, Reddit profile lookup
- **Phone**: Numverify phone validation and carrier information

## 🎯 Confidence Scoring

The system calculates confidence scores based on multiple factors:

### Scoring Components

1. **Google Search Analysis (35%)**
   - AI Summary availability: +30% base
   - Detailed description: +10%
   - Content richness: +10%
   - Knowledge Panel: +5%
   - Multiple verification sources: +10%
   - High relevance: +5%

2. **Blog/Article Analysis (15%)**
   - Relevance score: 40%
   - Content quality: 40%
   - Article count: 20%
   - Verification matches: +10%

3. **News Analysis (10%)**
   - Relevance score: 50%
   - Multiple sources: +20%
   - Article count: +20%
   - Recent articles: +10%

4. **Data Coverage (12-20%)**
   - Percentage of APIs returning data

5. **Consistency (12-15%)**
   - Cross-platform data consistency

6. **Verification (12-15%)**
   - Multi-source verification

7. **Data Quality (10%)**
   - Completeness, accuracy, relevance

### Confidence Levels

- **High (≥80%)**: Strong verification from multiple sources
- **Medium (50-79%)**: Good data with some verification
- **Low (30-49%)**: Limited data or inconsistent results
- **Very Low (<30%)**: Minimal or no data found

## 🔒 Risk Assessment

The system automatically assesses risk based on:

- **Threat Indicators**: Malware detection, suspicious patterns
- **Google AI Summary Analysis**: Keyword detection for threats
- **VirusTotal Results**: Malicious indicator counts
- **Data Consistency**: Low consistency may indicate identity mismatch
- **Multiple Accounts**: Potential fake account indicators

### Risk Levels

- **High (≥0.6)**: Multiple threat indicators, immediate investigation recommended
- **Medium (0.3-0.59)**: Some concerning indicators, further monitoring advised
- **Low (<0.3)**: No significant threat indicators

## 📸 Image Analysis

### Image Sources

1. **Google Knowledge Panel**: Entity images from Google
2. **Social Media**: Profile pictures from Twitter, Instagram, GitHub
3. **Blog Articles**: Images extracted from blog posts
4. **Search Results**: Images from Google search results

### Analysis Features

- **Face Detection**: Google Vision API face detection
- **Label Detection**: Automatic labeling (person, face, etc.)
- **Safe Search**: Content safety detection
- **Text Extraction**: OCR text extraction from images
- **Web Entity Detection**: Related web entities

## 🔧 Configuration

### API Keys

Add your API keys to `api_info` file:

```
API_KEY_X=your_twitter_api_key
API_KEY_SECRET_X=your_twitter_secret
GITHUB_API_TOKEN=your_github_token
api_key_for_numverify=your_numverify_key
api_key_virus_total=your_virustotal_key
api_newsApi.org=your_newsapi_key
google_news_api=your_google_news_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite+aiosqlite:///./osint.db
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
```

### Google Vision API

1. Create a Google Cloud Project
2. Enable Vision API
3. Create a service account
4. Download JSON credentials
5. Place as `service-account.json` in project root

## 📈 Performance

### Benchmarks

- **Data Collection**: 15-30 seconds for all APIs (parallel execution)
- **Blog/Article Scraping**: 10-25 seconds (depends on number of articles)
- **Google Search**: 3-5 seconds
- **Image Analysis**: 5-10 seconds (if Google Vision API enabled)
- **Analysis**: 3-5 seconds for confidence report
- **Dashboard Rendering**: <3 seconds
- **Concurrent Queries**: 50+ simultaneous queries
- **Total Workflow**: 30-60 seconds for standard queries

### Optimization Techniques

- **Parallel Execution**: All APIs called simultaneously
- **Intelligent Timeouts**: 5s per API, 15s for priority group, 25s for blog scraping
- **Caching**: Redis caching with 1-hour TTL
- **Lazy Loading**: Progressive data loading in frontend
- **Connection Pooling**: Optimized database connections
- **Async/Await**: Fully asynchronous backend for maximum throughput

### Optimization Features

- **Parallel API Calls**: Simultaneous requests to all APIs
- **Intelligent Timeouts**: 5s per API, 15s for priority group
- **Caching**: Redis caching with 1-hour TTL
- **Lazy Loading**: Progressive data loading
- **Connection Pooling**: Optimized database connections

## 🧪 Testing

### Test Endpoint

```bash
curl http://localhost:8000/api/test
```

Returns system status and supported query types.

### Example Search

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "John Doe", "query_type": "name"}'
```

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - System will run without caching
   - Check Redis is running: `redis-cli ping`

2. **API Rate Limits**
   - System handles rate limits automatically
   - Check API key quotas

3. **Google Vision API Errors**
   - Verify service account JSON is in root directory
   - Check API is enabled in Google Cloud Console

4. **Database Errors**
   - SQLite database is created automatically
   - Check file permissions: `chmod 664 osint.db`

## 📝 API Documentation

### Endpoints

- `POST /api/search`: Initiate a search
- `GET /api/profile/{profile_id}`: Get profile data
- `GET /api/test`: System status
- `WS /ws/{profile_id}`: WebSocket for real-time updates

### Request Format

```json
{
  "query": "search term",
  "query_type": "name|email|username|phone"
}
```

### Response Format

```json
{
  "profile_id": 1,
  "status": "complete",
  "query": "search term",
  "query_type": "name",
  "data": {
    "results": {...},
    "analysis": {...},
    "images": [...],
    "primary_image": {...}
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🔍 Data Sources

### Integrated APIs

1. **Twitter/X**: User profiles, tweets, follower counts
2. **Instagram**: Profile information, posts, followers (via API and Instaloader)
3. **GitHub**: User profiles, repositories, activity
4. **Reddit**: User profiles, posts, comments
5. **Hunter.io**: Email finder and domain analysis
6. **Numverify**: Phone number validation and carrier info
7. **VirusTotal**: Threat intelligence and malware detection
8. **Etherscan**: Blockchain address analysis
9. **NewsAPI**: News article search
10. **Google News**: News article aggregation
11. **Google Search**: AI summaries, Knowledge Panels, search results
12. **Telegram**: Username lookup (if available)
13. **IPInfo**: IP address geolocation
14. **Web Scraper**: Blog and article content extraction

### Analysis Sources

- **Google AI Summaries**: Comprehensive overviews from Google
- **Knowledge Panels**: Verified entity information
- **Blog Articles**: Deep-dive articles and blog posts
- **News Articles**: Recent news from multiple sources
- **Social Media**: Cross-platform profile correlation
- **Threat Intelligence**: VirusTotal and security indicators

## 🎨 Features in Detail

### 1. Google Search Integration
- Extracts AI summaries (like Google Assistant)
- Gets Knowledge Panel information
- Extracts entity images
- Retrieves "People Also Ask" questions
- Analyzes search result relevance

### 2. Blog & Article Analysis
- Searches Google for relevant blogs/articles
- Scrapes content from multiple articles
- Analyzes content quality and relevance
- Extracts images from articles
- Counts verification matches
- Measures content richness

### 3. News Article Analysis
- Aggregates articles from NewsAPI and Google News
- Analyzes relevance across all articles
- Tracks multiple news sources
- Identifies recent articles (last 30 days)
- Calculates source diversity

### 4. Image Analysis
- Extracts images from Google Knowledge Panel
- Gets profile pictures from social media
- Analyzes images with Google Vision API
- Detects faces and labels
- Matches images across sources
- Displays primary image prominently

### 5. Confidence Scoring
- Multi-factor analysis
- Weighted scoring system
- Minimum confidence guarantees
- Verification source counting
- Content quality assessment

### 6. Risk Assessment
- Threat keyword detection
- VirusTotal integration
- Suspicious pattern detection
- Multiple account detection
- Risk level classification

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Cloud Vision API
- Google Search (AI Summaries)
- All API providers (Twitter, Instagram, GitHub, etc.)
- FastAPI and React communities
- BeautifulSoup and aiohttp for web scraping

## 📧 Support

For issues and questions, please open an issue on GitHub.

## 🔒 Security & Privacy

- All API keys stored securely
- No data stored permanently (optional caching)
- Rate limiting implemented
- Input sanitization
- Secure WebSocket connections

## 🚀 Future Enhancements

- [ ] Additional API integrations
- [ ] Machine learning for pattern detection
- [ ] Advanced image recognition
- [ ] Real-time threat feeds
- [ ] Export functionality (PDF, CSV)
- [ ] Advanced filtering and search
- [ ] Batch processing
- [ ] API rate limit optimization

---

