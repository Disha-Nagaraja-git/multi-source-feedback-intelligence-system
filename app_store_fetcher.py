import pandas as pd
import feedparser
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def fetch_appstore_reviews(app_id: str, count: int = 50, country: str = 'us') -> pd.DataFrame:
    """
    Fetches recent reviews from Apple App Store RSS feed using feedparser.
    Expected RSS URL format: https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/xml
    Returns DataFrame with columns: ['id', 'date', 'rating', 'feedback_text', 'username', 'source']
    """
    try:
        # Construct RSS feed URL (Note: App Store API pagination via RSS can be limited, max 50 typically unless pages are traversed)
        # Using a JSON format feed could also be supported, but spec asks for RSS + feedparser
        # We'll use the Atom XML format that feedparser directly handles
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page=1/id={app_id}/sortBy=mostRecent/xml"
        
        logger.info(f"Fetching App Store reviews from RSS feed for id={app_id}")
        
        feed = feedparser.parse(url)
        
        if feed.bozo:
             logger.warning(f"Potential feed error: {feed.bozo_exception}")

        entries = feed.entries
        
        parsed_data = []
        # The first entry is usually the app metadata itself, so skip it if 'im_rating' is missing
        for entry in entries:
            # RSS namespace trickery: ratings are under 'im:rating'
            rating = entry.get('im_rating')
            if not rating:
                 continue
                 
            # Extract content (might contain HTML)
            content = entry.get('content', [{}])[0].get('value', entry.get('summary', ''))
            
            # Extract basic data
            row = {
                'id': entry.get('id', str(hash(content))),
                'date': pd.to_datetime(entry.get('updated', datetime.now())),
                'rating': int(rating),
                'feedback_text': content,
                'username': entry.get('author_detail', {}).get('name', 'Anonymous'),
                'source': 'Apple App Store'
            }
            parsed_data.append(row)
            
            if len(parsed_data) >= count:
                break
                
        df = pd.DataFrame(parsed_data)
        if df.empty:
            logger.warning(f"No App Store reviews found in RSS for {app_id}")
            return pd.DataFrame()
            
        return df[['id', 'date', 'rating', 'feedback_text', 'username', 'source']]

    except Exception as e:
        logger.error(f"Error fetching App Store reviews for {app_id}: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Whatsapp App Store ID = 310633997
    df = fetch_appstore_reviews('310633997', count=5)
    print(df.head())
