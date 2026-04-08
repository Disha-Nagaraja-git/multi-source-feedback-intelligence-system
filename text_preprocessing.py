import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Ensure NLTK resources are available
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("Downloading required NLTK data...")
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True) # for newer NLTK versions

STOP_WORDS = set(stopwords.words('english'))

def preprocess_text(text: str) -> str:
    """
    Cleans and preprocesses review text.
    - Lowercase
    - Remove punctuation and special characters
    - Remove stopwords
    - Extra whitespace removal
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove punctuation and numbers (keep only alphabets)
    text = re.sub(r'[^a-z\s]', ' ', text)
    
    # 3. Tokenize for stopword removal
    tokens = word_tokenize(text)
    
    # 4. Remove stopwords & short words
    filtered_tokens = [word for word in tokens if word not in STOP_WORDS and len(word) > 1]
    
    # 5. Join back into a single string
    return ' '.join(filtered_tokens).strip()

if __name__ == "__main__":
    # Test
    sample = "I REALLY love this app!!! But it crashes every 2 seconds. Fix it NOW! 😡 123"
    print(f"Original: {sample}")
    print(f"Processed: {preprocess_text(sample)}")
