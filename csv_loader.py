import pandas as pd
import uuid
import os
import logging

logger = logging.getLogger(__name__)

def load_csv_feedback(filepath: str) -> pd.DataFrame:
    """
    Loads custom survey feedback from a CSV file.
    Expected columns: feedback_text, rating, date
    """
    try:
        if not os.path.exists(filepath):
            logger.error(f"CSV file not found: {filepath}")
            return pd.DataFrame()
            
        df = pd.read_csv(filepath)
        
        # Check required columns (case insensitive, mapping to expected)
        cols_lower = {c.lower(): c for c in df.columns}
        
        # Flexibility in finding columns
        required_mappings = {
            'feedback_text': ['feedback_text', 'text', 'review', 'content'],
            'rating': ['rating', 'score', 'stars'],
            'date': ['date', 'time', 'timestamp']
        }
        
        final_mapping = {}
        missing = []
        
        for required, fallbacks in required_mappings.items():
            matched = False
            for fallback in fallbacks:
                if fallback in cols_lower:
                    final_mapping[required] = cols_lower[fallback]
                    matched = True
                    break
            if not matched:
                missing.append(required)
                
        if missing:
            logger.error(f"CSV is missing required data representations for: {missing}")
            return pd.DataFrame()
            
        # Build Standard DataFrame
        std_df = pd.DataFrame()
        
        if 'id' in cols_lower:
            std_df['id'] = df[cols_lower['id']].astype(str)
        else:
            std_df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
            
        std_df['date'] = pd.to_datetime(df[final_mapping['date']], errors='coerce')
        std_df['rating'] = pd.to_numeric(df[final_mapping['rating']], errors='coerce')
        std_df['feedback_text'] = df[final_mapping['feedback_text']].astype(str)
        std_df['source'] = 'CSV Survey'
        
        if 'username' in cols_lower:
            std_df['username'] = df[cols_lower['username']]
        else:
            std_df['username'] = 'Anonymous'
            
        # Drop rows with corrupted critical data
        std_df = std_df.dropna(subset=['date', 'rating', 'feedback_text'])
        
        logger.info(f"Successfully loaded {len(std_df)} entries from CSV")
        return std_df[['id', 'date', 'rating', 'feedback_text', 'username', 'source']]
        
    except Exception as e:
        logger.error(f"Error loading CSV data: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pass
