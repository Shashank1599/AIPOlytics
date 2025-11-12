# 🚀 IPO Analysis Dashboard

An AI-powered web application that provides comprehensive analysis of current and upcoming IPOs (Initial Public Offerings) using Google's Gemini AI model. This tool scrapes real-time IPO data and delivers structured insights through a beautiful, responsive web interface.

## 🌟 Features

### 📊 **Dual IPO Analysis**
- **Current IPOs**: Live IPOs available for investment
- **Upcoming IPOs**: Future IPOs scheduled for launch
- **Real-time Data**: Automatic data refresh with smart caching

### 🤖 **AI-Powered Insights**
- **Gemini AI Analysis**: Comprehensive IPO evaluation using Google's advanced AI
- **Structured Reports**: Analysis organized into clear sections:
  - IPO Snapshot (Size, Price Band, Dates)
  - Business Overview
  - Financial Health Assessment
  - Positive Investment Indicators
  - Risk Factors & Negative Indicators
  - AI-Generated Final Verdict

### 🎨 **Beautiful Web Interface**
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Modern UI**: Clean, professional design with gradient backgrounds
- **Interactive Dashboard**: Real-time statistics and easy navigation
- **Color-Coded Sections**: Visual distinction between current (green) and upcoming (orange) IPOs

### ⚡ **Smart Performance**
- **Intelligent Caching**: Reduces API calls and improves response times
- **Background Processing**: Non-blocking analysis with loading indicators
- **Error Handling**: Robust error management with user-friendly messages

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **AI/LLM**: Google Gemini AI, LangChain
- **Web Scraping**: Selenium WebDriver, BeautifulSoup4
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Data Source**: Chittorgarh.com IPO Dashboard
- **Environment**: Python Virtual Environment

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ 
- Google Gemini API Key
- Chrome browser (for Selenium WebDriver)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ipo-analysis-dashboard.git
   cd ipo-analysis-dashboard
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv llm_start
   llm_start\Scripts\activate
   
   # Linux/Mac
   python -m venv llm_start
   source llm_start/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

5. **Run the application**
   ```bash
   # Web Dashboard
   python app.py
   
   # Command Line Analysis
   python start.py
   ```

6. **Access the dashboard**
   Open your browser and navigate to: `http://localhost:5000`

## 🔧 Configuration

### Google Gemini API Setup
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add the key to your `.env` file as `GOOGLE_API_KEY`

### Chrome WebDriver
The application uses Chrome WebDriver for web scraping. Chrome will be automatically managed by Selenium, but ensure you have Chrome browser installed.

## 📱 Usage

### Web Dashboard
1. **Launch Application**: Run `python app.py`
2. **View IPOs**: Browse current and upcoming IPOs in separate sections
3. **Analyze IPO**: Click "Analyze with AI" on any IPO card
4. **Read Insights**: View comprehensive AI analysis in organized sections
5. **Refresh Data**: Use refresh button to get latest IPO information

### Command Line
1. **Run Analysis**: Execute `python start.py`
2. **Automated Processing**: Analyzes all current and upcoming IPOs sequentially
3. **Console Output**: Detailed analysis printed to terminal
4. **Structured Results**: Same analysis format as web interface

## 🏗️ Project Structure

AIPOlytics/
├── app.py
├── start.py
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/               # optional - for CSS/JS/


## 🔍 API Endpoints

The web application exposes several REST API endpoints:

- `GET /` - Main dashboard page
- `GET /api/ipos` - Fetch current and upcoming IPOs
- `GET /api/ipo/current/<index>/analyze` - Analyze current IPO
- `GET /api/ipo/upcoming/<index>/analyze` - Analyze upcoming IPO  
- `GET /api/refresh` - Force refresh IPO data

## 🛡️ Features in Detail

### Data Collection
- **Web Scraping**: Automated data collection from Chittorgarh.com
- **Anti-Scraping Bypass**: Selenium with headless Chrome
- **Data Parsing**: Intelligent HTML parsing with BeautifulSoup
- **Error Handling**: Robust timeout and retry mechanisms

### AI Analysis
- **Gemini Integration**: Latest Google AI model for analysis
- **Structured Prompts**: Optimized prompts for consistent output
- **LangChain Support**: Advanced LLM pipeline management
- **Context-Aware**: Analysis based on current market data

### Caching System
- **Smart Caching**: 1-hour cache for IPO data
- **Analysis Caching**: Persistent storage of analysis results
- **Memory Efficient**: Optimized data structures
- **Cache Invalidation**: Manual refresh capability

## 🚨 Important Notes

- **Rate Limiting**: Built-in delays to respect website rate limits
- **Data Accuracy**: Information accuracy depends on source website
- **Investment Disclaimer**: This tool is for informational purposes only
- **API Costs**: Gemini API usage may incur costs based on usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is designed for educational and informational purposes only. The IPO analysis provided by this application should not be considered as financial advice. Always conduct your own research and consult with financial advisors before making investment decisions.

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful language model capabilities
- **Chittorgarh.com** for IPO data source
- **Bootstrap** for responsive UI components
- **Flask** for lightweight web framework
- **LangChain** for LLM integration tools

## 📧 Contact

For questions, suggestions, or support, please open an issue on GitHub or contact [your-email@example.com].

---

**Happy IPO Analysis!** 🎯📈