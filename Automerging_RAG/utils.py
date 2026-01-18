"""
Utils module for Auto-merging Retrieval notebook
Contains helper functions for API keys
"""

import os

def get_openai_api_key():
    """
    Get OpenAI API key from environment variables
    
    Returns:
        str: OpenAI API key
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return api_key

def get_pinecone_api_key():
    """
    Get Pinecone API key from environment variables
    
    Returns:
        str: Pinecone API key
        
    Raises:
        ValueError: If PINECONE_API_KEY is not set
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY environment variable not set")
    return api_key
