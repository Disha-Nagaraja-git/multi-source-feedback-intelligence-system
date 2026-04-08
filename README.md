# Multi-Source Feedback Intelligence System

A production-ready Python project that aggregates, analyzes, and visualizes customer feedback from the Google Play Store, Apple App Store, and CSV survey files. 

## 🚀 Features
- **Multi-Source Fetching:** Scrapes live reviews from Google Play (`google-play-scraper`) and Apple App Store (`feedparser` via RSS).
- **Custom CSV Intake:** Upload custom survey data directly through the UI.
- **Sentiment Analysis:** Automatically classify feedback as Positive, Neutral, or Negative using `TextBlob`.
- **Trend Analysis:** Track sentiment over time to see if customer satisfaction is improving or declining.
- **Issue Detection:** Uses `scikit-learn` TF-IDF NLP techniques to extract the most frequently mentioned complaints, sorted by a calculated severity score.
- **Search & Filters:** Search reviews by keyword and filter by rating, source, and date range.
- **Modern Streamlit Dashboard:** Clean, interactive UI with filters, Plotly charts, and key metrics.
- **Export Data:** Download processed data as a CSV or generate a comprehensive Weekly Insights PDF report.

## 📁 Project Structure
```text
feedback_intelligence_system/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Project dependencies
├── README.md                   # This file
├── data_fetchers/              # Modules to fetch data from different sources
│   ├── google_play_fetcher.py
│   ├── app_store_fetcher.py
│   └── csv_loader.py
├── analysis/                   # NLP and data aggregation modules
│   ├── sentiment_analysis.py
│   ├── trend_analysis.py
│   └── issue_detection.py
├── reports/                    # PDF Generation logic
│   └── pdf_generator.py
├── utils/                      # Helper utilities
│   └── text_preprocessing.py
├── data/                       # Directory for sample data
└── assets/charts/              # Output directory for generated charts and PDFs
```

## 🛠️ Installation & Setup

1. **Clone the repository / navigate to the folder:**
   ```bash
   cd feedback_intelligence_system
   ```

2. **Create a Python Virtual Environment (Optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   > *Note: NLTK corpora (like stopwords) are downloaded automatically on the first run by `utils/text_preprocessing.py`.*

## 🏃‍♂️ How to Run

### Method 1: The Easiest Way (VS Code)
1. Open the project folder (`feedback_intelligence_system`) in VS Code.
2. Go to the **Run and Debug** view (`Cmd+Shift+D` on Mac or `Ctrl+Shift+D` on Windows).
3. Select **"Run Streamlit App"** from the top dropdown menu.
4. Click the green **Play** button (or press `F5`).

### Method 2: From the Terminal
Start the Streamlit dashboard by running:
```bash
cd feedback_intelligence_system  # Ensure you are inside the project folder
streamlit run app.py
```

The app will open automatically in your browser (usually `http://localhost:8501`).

### Using the App:
1. Open the sidebar to input App IDs.
   - For Google Play: Ex: `com.whatsapp`
   - For App Store: Ex: `310633997` (WhatsApp's numeric ID)
2. (Optional) Upload a CSV survey file. Expected columns: `date`, `rating`, `feedback_text`.
3. Click **"Run Analysis"**.
4. Use the filters to drill down into specific sentiment or sources.
5. Review the 'Top Complaints' table for actionable product insights.
6. Click **"Generate PDF Report"** to download a customized summary report.
