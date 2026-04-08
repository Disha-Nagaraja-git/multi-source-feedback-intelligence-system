import pandas as pd
import logging
from google_play_scraper import Sort, reviews

logger = logging.getLogger(__name__)

def fetch_playstore_reviews(app_id: str, count: int = 100, lang: str = 'en', country: str = 'us') -> pd.DataFrame:
    """
    Fetches latest reviews from Google Play Store.
    Returns DataFrame with columns: ['id', 'date', 'rating', 'feedback_text', 'username', 'source']
    """
    try:
        logger.info(f"Fetching up to {count} Play Store reviews for {app_id}")
        result, _ = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=count
        )
        
        if not result:
            logger.warning(f"No Play Store reviews found for {app_id}")
            return pd.DataFrame()
            
        df = pd.DataFrame(result)
        
        # Standardize schema to match requirements
        df['source'] = 'Google Play'
        
        # Rename essential columns
        df = df.rename(columns={
            'reviewId': 'id',
            'at': 'date',      # Datetime object
            'score': 'rating',
            'content': 'feedback_text',
            'userName': 'username'
        })
        
        # Ensure only standardized columns are returned
        return df[['id', 'date', 'rating', 'feedback_text', 'username', 'source']]
        
    except Exception as e:
        logger.error(f"Error fetching Play Store reviews for {app_id}: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = fetch_playstore_reviews('com.whatsapp', count=5)
    print(df)
