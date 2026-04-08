import pandas as pd
from textblob import TextBlob
import logging

logger = logging.getLogger(__name__)

def analyze_sentiment(df: pd.DataFrame, text_column: str = 'feedback_text') -> pd.DataFrame:
    """
    Analyzes sentiment of text in a DataFrame using TextBlob.
    Adds 'sentiment_score' (-1.0 to 1.0) and 'sentiment_label' (Positive, Neutral, Negative).
    Requires a column containing the text.
    """
    if df.empty or text_column not in df.columns:
        logger.warning(f"Cannot analyze sentiment: DataFrame is empty or {text_column} missing.")
        return df
        
    def get_sentiment(text):
        if not isinstance(text, str) or not text.strip():
            return 0.0, 'Neutral'
            
        blob = TextBlob(text)
        score = blob.sentiment.polarity
        
        # Determine label based on threshold
        if score > 0.1:
            label = 'Positive'
        elif score < -0.1:
            label = 'Negative'
        else:
            label = 'Neutral'
            
        return score, label
        
    try:
        logger.info("Performing sentiment analysis...")
        
        # Apply the function to the text column
        sentiment_results = df[text_column].apply(get_sentiment)
        
        # Unpack the tuple results into separate columns
        df['sentiment_score'] = [res[0] for res in sentiment_results]
        df['sentiment_label'] = [res[1] for res in sentiment_results]
        
        return df
    except Exception as e:
        logger.error(f"Error during sentiment analysis: {str(e)}")
        # Provide fallback columns if it fails midway
        if 'sentiment_score' not in df.columns:
            df['sentiment_score'] = 0.0
        if 'sentiment_label' not in df.columns:
             df['sentiment_label'] = 'Neutral'
        return df

if __name__ == "__main__":
    # Test
    sample_df = pd.DataFrame({'feedback_text': ["Great app!", "Terrible experience crashing.", "It's okay I guess."]})
    res_df = analyze_sentiment(sample_df)
    print(res_df)
