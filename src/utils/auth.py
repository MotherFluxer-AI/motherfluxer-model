import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_token(token: str) -> bool:
    """
    Verify the token against the AUTH_TOKEN from environment variables
    """
    if not token:
        return False
    
    expected_token = os.getenv("AUTH_TOKEN")
    return token == expected_token

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