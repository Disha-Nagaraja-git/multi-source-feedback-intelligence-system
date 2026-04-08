import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)

def detect_issues(df: pd.DataFrame, text_column: str = 'processed_text', top_n: int = 10) -> pd.DataFrame:
    """
    Detects frequently mentioned problems using TF-IDF on negative sentiment reviews.
    Requires text to be already preprocessed (lowercase, no stopwords).
    Returns a DataFrame of top keywords and their severity scores.
    """
    if df.empty or text_column not in df.columns or 'sentiment_label' not in df.columns:
        logger.warning("Missing required columns for issue detection (need processed text and sentiment label).")
        return pd.DataFrame()

    try:
        # 1. Filter for Negative Reviews
        negative_df = df[df['sentiment_label'] == 'Negative'].copy()
        
        if negative_df.empty:
            logger.info("No negative reviews found. No issues detected.")
            return pd.DataFrame(columns=['issue_keyword', 'frequency', 'avg_negative_sentiment', 'severity_score'])
            
        # Ensure we have valid text
        texts = negative_df[text_column].fillna('').tolist()
        texts = [t for t in texts if isinstance(t, str) and t.strip()]
        
        if not texts:
            return pd.DataFrame(columns=['issue_keyword', 'frequency', 'avg_negative_sentiment', 'severity_score'])

        # 2. Extract Keywords using TF-IDF
        # We'll use absolute frequency (CountVectorizer logic) for frequency, 
        # but TF-IDF helps surface important unique terms. 
        # For simplicity and robust issue counting, extracting single words/bigrams using TF-IDF sum.
        vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Get feature names and sum of tfidf scores across all negative reviews
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.sum(axis=0).A1
        
        # Map back to keywords
        keyword_scores = zip(feature_names, tfidf_scores)
        sorted_keywords = sorted(keyword_scores, key=lambda x: x[1], reverse=True)[:top_n*2]
        
        # 3. Calculate metrics for these top keywords
        results = []
        for kw, _ in sorted_keywords[:top_n]:
            # Find reviews containing this keyword
            # Using simple substring match on processed text
            contains_kw_mask = negative_df[text_column].str.contains(kw, case=False, na=False)
            kw_df = negative_df[contains_kw_mask]
            
            freq = len(kw_df)
            if freq > 0:
                # Average negativity (sentiment_score is negative, so min or mean is negative)
                # To make severity score positive and higher = worse, we take absolute value or multiply by -1
                avg_neg = kw_df['sentiment_score'].mean()
                
                # severity_score = frequency_of_issue * negative_sentiment_score (absolute)
                severity = freq * abs(avg_neg)
                
                results.append({
                    'issue_keyword': kw,
                    'frequency': freq,
                    'avg_negative_sentiment': avg_neg,
                    'severity_score': severity
                })
                
        results_df = pd.DataFrame(results)
        
        if not results_df.empty:
            # Sort by severity score descending
            results_df = results_df.sort_values('severity_score', ascending=False).reset_index(drop=True)
            
        return results_df
        
    except Exception as e:
        logger.error(f"Error during issue detection: {str(e)}")
        return pd.DataFrame(columns=['issue_keyword', 'frequency', 'avg_negative_sentiment', 'severity_score'])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pass
