import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
from datetime import datetime

# Import modules
from data_fetchers.google_play_fetcher import fetch_playstore_reviews
from data_fetchers.app_store_fetcher import fetch_appstore_reviews
from data_fetchers.csv_loader import load_csv_feedback
from utils.text_preprocessing import preprocess_text
from analysis.sentiment_analysis import analyze_sentiment
from analysis.trend_analysis import calculate_daily_sentiment, get_overall_metrics
from analysis.issue_detection import detect_issues
from reports.pdf_generator import export_weekly_report

# Page Config
st.set_page_config(
    page_title="Multi-Source Feedback Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #1E1E1E;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-value { font-size: 2rem; font-weight: bold; }
    .metric-title { font-size: 1rem; color: #b0b0b0; }
    </style>
""", unsafe_allow_html=True)

# --- Caching Data Fetchers ---
@st.cache_data(ttl=3600)
def get_playstore_data(app_id, count):
    return fetch_playstore_reviews(app_id, count)

@st.cache_data(ttl=3600)
def get_appstore_data(app_id, count):
    return fetch_appstore_reviews(app_id, count)

# --- State Management ---
if 'df_raw' not in st.session_state:
    st.session_state['df_raw'] = pd.DataFrame()
if 'df_processed' not in st.session_state:
    st.session_state['df_processed'] = pd.DataFrame()

def process_and_merge(new_df):
    if new_df.empty:
        return
        
    # Preprocess
    new_df['processed_text'] = new_df['feedback_text'].apply(preprocess_text)
    # Analyze sentiment
    new_df = analyze_sentiment(new_df, text_column='processed_text')
    
    # Merge into existing state
    if st.session_state['df_processed'].empty:
        st.session_state['df_processed'] = new_df
    else:
        combined = pd.concat([st.session_state['df_processed'], new_df], ignore_index=True)
        # remove exact duplicates if necessary based on ID
        combined = combined.drop_duplicates(subset=['id'], keep='first')
        st.session_state['df_processed'] = combined

# --- Sidebar Navigation ---
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", [
    "Overview Dashboard",
    "Fetch Reviews",
    "Upload CSV",
    "Sentiment Analysis",
    "Trend Analysis",
    "Issue Detection",
    "Generate Report"
])

# --- Main App Logic ---
st.title("📈 Multi-Source Feedback Intelligence System")

df = st.session_state.get('df_processed', pd.DataFrame())

if page == "Overview Dashboard":
    st.markdown("### 📊 Overview Dashboard")
    
    if df.empty:
        st.info("No data available. Please go to **Fetch Reviews** or **Upload CSV** to load data.")
    else:
        # Metrics
        metrics = get_overall_metrics(df)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Total Reviews</div><div class="metric-value">{metrics["total_reviews"]}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Avg Sentiment</div><div class="metric-value">{metrics["avg_sentiment"]:.2f}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Positive %</div><div class="metric-value" style="color: #4CAF50;">{metrics["pct_positive"]:.1f}%</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Negative %</div><div class="metric-value" style="color: #F44336;">{metrics["pct_negative"]:.1f}%</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Filter & Search Reviews")
        search_query = st.text_input("Search reviews for keywords:", placeholder="e.g., crash, amazing...")
        
        col1, col2 = st.columns(2)
        with col1:
            sources = df['source'].unique().tolist()
            selected_sources = st.multiselect("Source Filter", options=sources, default=sources)
        with col2:
            sentiments = df['sentiment_label'].unique().tolist()
            selected_sentiments = st.multiselect("Sentiment Filter", options=sentiments, default=sentiments)
            
        filtered_df = df[
            (df['source'].isin(selected_sources)) &
            (df['sentiment_label'].isin(selected_sentiments))
        ]
        
        if search_query:
            filtered_df = filtered_df[filtered_df['feedback_text'].str.contains(search_query, case=False, na=False)]
            
        st.markdown(f"**Showing {len(filtered_df)} reviews**")
        st.dataframe(filtered_df[['date', 'source', 'rating', 'sentiment_label', 'sentiment_score', 'feedback_text']].head(50), use_container_width=True)

        # Export CSV Button
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Export Filtered Data to CSV",
            data=csv_data,
            file_name=f"Processed_Feedback_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            type="primary"
        )

elif page == "Fetch Reviews":
    st.markdown("### 📥 Fetch Live Reviews")
    st.write("Extract live feedback directly from app stores via API and RSS.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Google Play Store")
        play_id = st.text_input("App Package Name", value="com.whatsapp", help="e.g. com.facebook.katana")
        play_limit = st.slider("Number of reviews (Android)", 10, 200, 50, key="play_limit")
        if st.button("Fetch Play Store Reviews", type="primary"):
            with st.spinner(f"Fetching {play_limit} reviews for {play_id}..."):
                play_df = get_playstore_data(play_id, play_limit)
                if not play_df.empty:
                    process_and_merge(play_df)
                    st.success(f"Successfully loaded {len(play_df)} Play Store reviews!")
                else:
                    st.error("Failed to fetch Play Store reviews. Check the App ID.")
                    
    with col2:
        st.markdown("#### Apple App Store")
        ios_id = st.text_input("App Store ID", value="310633997", help="Numeric id, e.g. 310633997")
        ios_limit = st.slider("Number of reviews (iOS)", 10, 200, 50, key="ios_limit")
        if st.button("Fetch App Store Reviews", type="primary"):
            with st.spinner(f"Fetching {ios_limit} reviews from RSS for id={ios_id}..."):
                 ios_df = get_appstore_data(ios_id, ios_limit)
                 if not ios_df.empty:
                     process_and_merge(ios_df)
                     st.success(f"Successfully loaded {len(ios_df)} App Store reviews!")
                 else:
                     st.error("Failed to fetch App Store reviews. Check the App ID or connectivity.")

elif page == "Upload CSV":
    st.markdown("### 📁 Upload Survey CSV")
    st.write("Upload exported survey results from Typeform, SurveyMonkey, etc.")
    st.info("Expected columns: `feedback_text`, `rating`, `date`")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    if uploaded_file is not None:
        try:
            # Save temporarily to read using our loader
            temp_path = os.path.join("data", "uploaded_temp.csv")
            os.makedirs("data", exist_ok=True)
            with open(temp_path, "wb") as f:
                 f.write(uploaded_file.getbuffer())
                 
            st.write("Preview:")
            preview_df = pd.read_csv(temp_path).head(3)
            st.dataframe(preview_df)
                 
            if st.button("Process & Import CSV Data", type="primary"):
                 with st.spinner("Processing CSV..."):
                     csv_df = load_csv_feedback(temp_path)
                     if not csv_df.empty:
                         process_and_merge(csv_df)
                         st.success(f"Successfully processed and imported {len(csv_df)} records!")
                     else:
                         st.error("Failed to import CSV. Please ensure it has the required columns.")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

elif page == "Sentiment Analysis":
    st.markdown("### 🎭 Sentiment Analysis")
    if df.empty:
        st.warning("No data available.")
    else:
        st.write("Natural Language Processing (TextBlob/VADER) classifies reviews as Positive, Neutral, or Negative.")
        
        col1, col2 = st.columns(2)
        with col1:
             st.markdown("#### Sentiment Distribution")
             pie_fig = px.pie(
                 df, names='sentiment_label', 
                 color='sentiment_label',
                 color_discrete_map={'Positive': '#4CAF50', 'Neutral': '#9E9E9E', 'Negative': '#F44336'},
                 hole=0.4
             )
             st.plotly_chart(pie_fig, use_container_width=True)
             
        with col2:
             st.markdown("#### Rating vs Sentiment Relationship")
             if 'rating' in df.columns:
                 # Group by rating to show avg sentiment
                 rating_df = df.groupby('rating', as_index=False).agg(avg_sentiment=('sentiment_score', 'mean'), count=('id', 'count'))
                 bar_fig = px.bar(
                     rating_df, x='rating', y='avg_sentiment', 
                     color='avg_sentiment',
                     color_continuous_scale='RdYlGn',
                     labels={'rating': 'Star Rating', 'avg_sentiment': 'Avg Sentiment Score'}
                 )
                 st.plotly_chart(bar_fig, use_container_width=True)
                 
        st.markdown("#### Latest Processed Feedback Table")
        st.dataframe(df[['date', 'rating', 'sentiment_label', 'sentiment_score', 'feedback_text']].sort_values('date', ascending=False).head(20), use_container_width=True)

elif page == "Trend Analysis":
    st.markdown("### 📈 Sentiment Trend Analysis")
    if df.empty:
        st.warning("No data available.")
    else:
        df_trend = calculate_daily_sentiment(df)
        if not df_trend.empty:
            st.write("Track how customer satisfaction fluctuates over time.")
            line_fig = px.line(
                 df_trend, x='date', y='avg_sentiment', 
                 markers=True, 
                 labels={"date": "Date", "avg_sentiment": "Average Sentiment Score"}
             )
            line_fig.add_hline(y=0, line_dash="dot", annotation_text="Neutral", annotation_position="bottom right")
            st.plotly_chart(line_fig, use_container_width=True)
             
            st.markdown("#### Volume Trend")
            bar_fig = px.bar(df_trend, x='date', y='review_count', labels={"date": "Date", "review_count": "Number of Reviews"})
            st.plotly_chart(bar_fig, use_container_width=True)
        else:
             st.info("Not enough data to map trends.")

elif page == "Issue Detection":
    st.markdown("### 🚨 Issue Detection & Priority Routing")
    if df.empty:
        st.warning("No data available.")
    else:
        st.write("Calculates TF-IDF scores on negative reviews to highlight the most severe and frequent bugs/feature requests.")
        
        with st.spinner("Extracting Keywords..."):
            df_issues = detect_issues(df)
            
        if not df_issues.empty:
            st.markdown("#### Top Detected Issues (Ranked by Severity)")
            st.dataframe(
                df_issues.style.background_gradient(subset=['severity_score'], cmap='Reds'),
                use_container_width=True
            )
            
            # Simple bar chart of top issues
            issue_fig = px.bar(
                df_issues.head(10), x='issue_keyword', y='severity_score',
                color='frequency',
                labels={'issue_keyword': 'Detected Keyword/Phrase', 'severity_score': 'Severity Score'}
            )
            st.plotly_chart(issue_fig, use_container_width=True)
        else:
            st.success("No critical negative issues found in the current dataset!")

elif page == "Generate Report":
    st.markdown("### 📑 Generate Weekly PDF Report")
    if df.empty:
        st.warning("No data available. Load data to generate a report.")
    else:
        st.write("Compile all metrics, trends, and top issues into a professional, downloadable PDF summary.")
        
        if st.button("Generate & Download PDF Report", type="primary"):
            with st.spinner("Compiling PDF..."):
                 metrics = get_overall_metrics(df)
                 df_trend = calculate_daily_sentiment(df)
                 df_issues = detect_issues(df)
                 
                 pdf_path = export_weekly_report(metrics, df_trend, df_issues)
                 if pdf_path and os.path.exists(pdf_path):
                     with open(pdf_path, "rb") as pdf_file:
                         st.download_button(
                             label="⬇️ Download PDF Report Link",
                             data=pdf_file,
                             file_name=f"Feedback_Intel_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                             mime="application/pdf"
                         )
                     st.success("Report Generated Successfully! Click the button above to download.")
                 else:
                     st.error("Failed to generate report.")
                     
        with st.expander("PDF Contents Preview"):
             st.write("**Included in the report:**")
             st.write("- Overview Statistics (Total Reviews, Avg Sentiment, % Positive/Negative)")
             st.write("- Sentiment Trend Chart showing data over time")
             st.write("- Top prioritizing complaints ranked by severity")
