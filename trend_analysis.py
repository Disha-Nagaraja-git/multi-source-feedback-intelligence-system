import pandas as pd
import logging

logger = logging.getLogger(__name__)

def calculate_daily_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the daily average sentiment and count of reviews.
    Groups by the 'date' column (normalized to just the date, ignoring time).
    """
    if df.empty or 'date' not in df.columns or 'sentiment_score' not in df.columns:
        logger.warning("Missing required columns for trend analysis.")
        return pd.DataFrame()
        
    try:
        # Create a copy so we don't modify the original dataframe unexpectedly
        df_trend = df.copy()
        
        # Ensure date is datetime and normalize to start of day
        df_trend['date'] = pd.to_datetime(df_trend['date']).dt.floor('D')
        
        # Group by date
        daily_trend = df_trend.groupby('date').agg(
            avg_sentiment=('sentiment_score', 'mean'),
            review_count=('id', 'count'),
            positive_count=('sentiment_label', lambda x: (x == 'Positive').sum()),
            negative_count=('sentiment_label', lambda x: (x == 'Negative').sum())
        ).reset_index()
        
        # Sort chronologically
        daily_trend = daily_trend.sort_values('date')
        
        return daily_trend
        
    except Exception as e:
        logger.error(f"Error calculating daily sentiment: {str(e)}")
        return pd.DataFrame()

def get_overall_metrics(df: pd.DataFrame) -> dict:
    """
    Returns general statistics formatting into a dictionary.
    """
    metrics = {
        'total_reviews': 0,
        'avg_rating': 0.0,
        'avg_sentiment': 0.0,
        'pct_positive': 0.0,
        'pct_negative': 0.0
    }
    
    if df.empty:
        return metrics
        
    try:
        total = len(df)
        metrics['total_reviews'] = total
        
        if 'rating' in df.columns:
            metrics['avg_rating'] = df['rating'].mean()
            
        if 'sentiment_score' in df.columns:
            metrics['avg_sentiment'] = df['sentiment_score'].mean()
            
        if 'sentiment_label' in df.columns:
            pos_ct = (df['sentiment_label'] == 'Positive').sum()
            neg_ct = (df['sentiment_label'] == 'Negative').sum()
            metrics['pct_positive'] = (pos_ct / total) * 100
            metrics['pct_negative'] = (neg_ct / total) * 100
            
    except Exception as e:
        logger.error(f"Error calculating overall metrics: {str(e)}")
        
    return metrics
