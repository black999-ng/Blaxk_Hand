# aiLEADS 🚀

**AI-Powered Lead Generation System** — Scrape, analyze, and engage high-quality business leads with intelligent automation.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

---

## 📋 Overview

aiLEADS is an intelligent lead generation platform that combines:
- **Google Maps Web Scraping** — Extract business data at scale
- **AI-Powered Analysis** — Score leads using Google Gemini AI
- **Smart Messaging** — Generate personalized WhatsApp outreach
- **Lead Management** — Track, deduplicate, and organize prospects
- **Multi-Profile Support** — Rotate browser profiles to avoid detection

Perfect for sales teams, business development, and marketing automation.

---

## ✨ Key Features

- 🔍 **Google Maps Scraper** — Extract business names, ratings, reviews, contact info, and websites
- 🤖 **AI Lead Scoring** — Intelligent ranking with custom WhatsApp openers and pain point analysis using Gemini
- 📊 **Lead Management** — Automatic deduplication, Excel export, and JSON logging
- 💬 **WhatsApp Integration** — AI-generated personalized messages for outreach
- 🖥️ **Beautiful CLI** — Rich terminal interface with progress tracking
- 🔄 **Profile Rotation** — Multiple browser profiles to prevent detection
- 📈 **Session Tracking** — Complete audit trail of scraping and outreach activity

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key
- Chrome/Chromium browser

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/black999-ng/aiLEADS.git
   cd aiLEADS
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
   Or create a `.env` file:
   ```env
   GEMINI_API_KEY=your-api-key-here
   ```

### Basic Usage

```bash
python main.py
```

The CLI will guide you through:
1. Selecting or creating a search location
2. Defining search queries (e.g., "restaurants", "plumbers")
3. Running the scraper with Google Maps
4. Analyzing results with AI
5. Generating WhatsApp messages

---

## 📁 Project Structure

```
aiLEADS/
├── main.py                 # Main orchestrator
├── aileads.py             # Database setup & AI analysis
├── scraper.py             # Google Maps web scraper
├── analyzer.py            # Lead ranking and filtering
├── message_generator.py    # AI-powered message creation
├── profile_manager.py      # Browser profile management
├── cli_interface.py        # Terminal UI
├── send_whatsapp.py       # WhatsApp messaging
├── diagnose.py            # Diagnostic tools
│
├── chrome_profiles/        # Browser profiles for scraping
├── messages/               # Message templates
├── output/                 # Generated leads & logs
│   ├── top_leads.xlsx
│   ├── message_history.json
│   ├── sent_log.json
│   └── session_*.json
│
├── whatsapp_bot/           # WhatsApp bot (Node.js)
│   ├── bot.js
│   ├── history_manager.js
│   ├── package.json
│   └── auth_info_baileys/  # WhatsApp credentials
│
├── requirements.txt
└── README.md
```

---

## 🛠️ Core Components

### 1. **GoogleMapsScraper** (`scraper.py`)
Extracts business data from Google Maps with anti-detection measures:
```python
from scraper import GoogleMapsScraper

scraper = GoogleMapsScraper(location="New York", headless=True)
results = scraper.scrape_multiple_queries(["restaurants", "cafes"])
```

**Returns:**
- Business name, category, rating, review count
- Phone number, website, address
- Google Maps URL

### 2. **BusinessAnalyzer** (`analyzer.py`)
Scores and ranks leads using Google's Gemini AI:
```python
from analyzer import BusinessAnalyzer

analyzer = BusinessAnalyzer()
ranked_leads = analyzer.analyze_businesses(scraped_businesses)
```

**Generates:**
- Lead score (0-100)
- Custom WhatsApp opener
- Pain point hypothesis

### 3. **MessageGenerator** (`message_generator.py`)
Creates personalized AI-powered messages:
- Dynamic tone and style
- Industry-specific messaging
- Template-based generation

### 4. **ProfileManager** (`profile_manager.py`)
Manages Chrome browser profiles:
- Creates isolated profiles for scraping
- Rotates profiles to avoid detection
- Configures anti-bot headers

### 5. **BLAXKCLI** (`cli_interface.py`)
Beautiful command-line interface with:
- ASCII art banners
- Progress bars and spinners
- Rich table formatting
- Interactive prompts

---

## 📊 Output Formats

### Excel Export (`top_leads.xlsx`)
Clean, organized lead data ready for sales teams:
- Business info, contact details
- Lead scores and ratings
- AI-generated openers
- Outreach status

### JSON Logs
- `message_history.json` — All generated messages
- `sent_log.json` — WhatsApp delivery status
- `session_*.json` — Complete session records

---

## 🤖 AI Integration

aiLEADS uses **Google Gemini AI** for intelligent lead analysis:

```python
class LeadAnalysis(BaseModel):
    lead_score: int          # 0-100 ranking
    reasoning: str           # Why this score
    custom_whatsapp_opener: str  # Personalized message
    pain_point_hypothesis: str   # Target's likely needs
```

### Filtering Logic
- ✅ Businesses with websites preferred
- ✅ Good ratings (customizable threshold)
- ✅ Active, engaged businesses
- ❌ Duplicates automatically removed

---

## 💬 WhatsApp Integration

Two methods for outreach:

### 1. **Python (Selenium-based)**
```python
from send_whatsapp import WhatsAppSender

sender = WhatsAppSender()
sender.send_message(phone_number, personalized_message)
```

### 2. **Node.js Bot (Baileys)**
Real WhatsApp Web automation:
```bash
cd whatsapp_bot
npm install
node bot.js
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)
```env
# Required
GEMINI_API_KEY=your-api-key-here

# Optional
CHROME_PATH=/path/to/chrome
HEADLESS=true
PROFILE_ROTATION=true
MAX_RETRIES=3
```

### Search Configuration
Customize in the CLI or via code:
```python
search_queries = ["plumbers", "electricians", "contractors"]
location = "Los Angeles"
max_results = 500
```

---

## 📈 Workflow

```
1. SCRAPE (Google Maps)
   ↓
2. ANALYZE (AI Scoring)
   ↓
3. FILTER (Quality Control)
   ↓
4. DEDUPLICATE (Remove Duplicates)
   ↓
5. GENERATE MESSAGES (AI Writing)
   ↓
6. EXPORT (Excel + JSON)
   ↓
7. SEND (WhatsApp Outreach)
   ↓
8. TRACK (Session Logs)
```

---

## 🔒 Safety & Compliance

- ✅ Browser profile rotation to avoid detection
- ✅ Randomized delays between requests
- ✅ Anti-bot headers and fingerprinting evasion
- ✅ Respectful scraping practices
- ⚠️ Always comply with Google Maps ToS and local laws

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `google-maps-scraper` | Google Maps data extraction |
| `playwright` | Browser automation |
| `google-generativeai` | Gemini AI integration |
| `pandas` | Data processing |
| `openpyxl` | Excel export |
| `python-dotenv` | Environment variables |

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

## ⚠️ Disclaimer

This tool is for educational and legitimate business purposes. Users are responsible for:
- Complying with Google's Terms of Service
- Respecting data privacy laws (GDPR, CCPA, etc.)
- Following WhatsApp's usage policies
- Legal compliance in their jurisdiction

Misuse of this tool for spam or unauthorized data collection is prohibited.

---

## 🆘 Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure your `.env` file is in the project root
- Check that the key is valid: `echo $GEMINI_API_KEY`

### Scraper getting blocked
- Enable profile rotation: `profile_manager.create_profile()`
- Add delays: increase `time.sleep()` values
- Use different locations

### WhatsApp connection issues
- Ensure QR code is scanned before timeout
- Check internet connectivity
- Verify WhatsApp Web is accessible in your region

---

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/yourusername/aiLEADS/issues)
- Check existing documentation
- Review session logs in `output/`

---

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] SMS outreach integration
- [ ] Email campaign builder
- [ ] Advanced filtering rules
- [ ] Dashboard UI
- [ ] Webhook integrations
- [ ] CRM connectors

---

**Made with ❤️ by BLAXK**

⭐ If this project helps you, please consider starring it on GitHub!
