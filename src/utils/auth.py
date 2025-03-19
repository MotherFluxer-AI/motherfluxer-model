import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def verify_token(token: str) -> bool:
    """
    Verify a token against the auth_token from environment variables
    """
    if not token:
        logger.debug("No token provided for verification")
        return False
        
    # Get token from environment variables
    env_token = os.getenv('auth_token')
    if not env_token:
        logger.debug("No auth_token found in environment variables")
        return False
        
    logger.debug(f"Comparing tokens - Provided: {token}, Environment: {env_token}")
    return token == env_token

def extract_token_from_header(auth_header: Optional[str]) -> Optional[str]:
    """
    Extract token from Authorization header
    """
    if not auth_header:
        return None
        
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
        
    return parts[1] 