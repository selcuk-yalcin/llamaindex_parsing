"""
API Keys Configuration Module
This module loads API keys from environment variables or .env file
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class APIKeys:
    """Class to manage API keys"""
    
    @staticmethod
    def get_openai_api_key():
        """Get OpenAI API key from environment"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            raise ValueError("Please set OPENAI_API_KEY in .env file")
        return api_key
    
    @staticmethod
    def get_anthropic_api_key():
        """Get Anthropic (Claude/Sonnet) API key from environment"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_anthropic_api_key_here':
            raise ValueError("Please set ANTHROPIC_API_KEY in .env file")
        return api_key
    
    @staticmethod
    def get_pinecone_api_key():
        """Get Pinecone API key from environment"""
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key or api_key == 'your_pinecone_api_key_here':
            raise ValueError("Please set PINECONE_API_KEY in .env file")
        return api_key

# Example usage
if __name__ == "__main__":
    keys = APIKeys()
    
    try:
        openai_key = keys.get_openai_api_key()
        print("✓ OpenAI API key loaded successfully")
    except ValueError as e:
        print(f"✗ OpenAI: {e}")
    
    try:
        anthropic_key = keys.get_anthropic_api_key()
        print("✓ Anthropic API key loaded successfully")
    except ValueError as e:
        print(f"✗ Anthropic: {e}")
    
    try:
        pinecone_key = keys.get_pinecone_api_key()
        print("✓ Pinecone API key loaded successfully")
    except ValueError as e:
        print(f"✗ Pinecone: {e}")
