"""
Configuration Settings
OpenRouter, LlamaParse and MongoDB settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Main configuration class"""
    
    # OpenRouter API Settings
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # LLM Models to use (from OpenRouter)
    # Recommended models:
    # - anthropic/claude-3.5-sonnet (Most powerful, for complex hierarchies)
    # - google/gemini-2.5-flash-lite (Fast, low cost, good for structured output)
    # - google/gemini-pro-1.5 (For long documents, 1M token context)
    # - openai/gpt-4-turbo (Balanced performance/cost)
    # - qwen/qwen-2.5-72b-instruct (Low cost, good performance)
    DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")
    
    # LlamaParse API Settings
    LLAMAPARSE_API_KEY = os.getenv("LLAMAPARSE_API_KEY", "")
    LLAMAPARSE_RESULT_TYPE = "markdown"  # or "text"
    LLAMAPARSE_LANGUAGE = "tr"  # For Turkish documents
    LLAMAPARSE_PREMIUM_MODE = True  # Better table and layout analysis
    
    # MongoDB Settings (optional - to store extracted data)
    MONGODB_URI = os.getenv("MONGODB_URI", "")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "legal_documents")
    MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "extracted_laws")
    
    # File Paths
    BASE_DIR = Path(__file__).parent
    INPUT_DIR = BASE_DIR / "data" / "input"
    OUTPUT_DIR = BASE_DIR / "data" / "output"
    PARSED_DIR = BASE_DIR / "parsed_markdown"
    EXTRACTED_DIR = BASE_DIR / "extracted_laws"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Processing Settings
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "3"))  # Number of workers for parallel processing
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "50000"))  # Chunk size for long documents
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5"))  # For batch processing
    
    # Retry Settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))  # seconds
    
    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate(cls):
        """Validate required configurations"""
        errors = []
        
        if not cls.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY not found!")
        
        if not cls.LLAMAPARSE_API_KEY:
            errors.append("LLAMAPARSE_API_KEY not found!")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))
        
        return True
    
    @classmethod
    def create_directories(cls):
        """Create required directories"""
        for directory in [cls.INPUT_DIR, cls.OUTPUT_DIR, cls.PARSED_DIR, 
                         cls.EXTRACTED_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Test configuration
if __name__ == "__main__":
    try:
        Config.validate()
        Config.create_directories()
        print(" Configuration valid!")
        print(f" Directories created")
        print(f" Model: {Config.DEFAULT_MODEL}")
        print(f" LlamaParse mode: {'Premium' if Config.LLAMAPARSE_PREMIUM_MODE else 'Standard'}")
    except ValueError as e:
        print(f" {e}")

