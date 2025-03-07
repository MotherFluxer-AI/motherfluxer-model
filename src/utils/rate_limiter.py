from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List
import time

class RateLimiter:
    def __init__(self, messages_per_minute: int = 5):
        self.messages_per_minute = messages_per_minute
        self.client_messages: Dict[str, List[float]] = defaultdict(list)
        print(f"Initializing RateLimiter with {messages_per_minute} messages per minute")  # Debug print
    
    def can_send_message(self, client_id: str) -> bool:
        """Check if client can send a message based on rate limit"""
        now = time.time()
        
        # Remove messages older than 1 minute
        current_messages = [
            timestamp for timestamp in self.client_messages[client_id]
            if now - timestamp < 60
        ]
        self.client_messages[client_id] = current_messages
        
        # Debug prints
        print(f"\nRate limit check for client {client_id}:")
        print(f"Current message count: {len(current_messages)}")
        print(f"Messages per minute limit: {self.messages_per_minute}")
        
        # Check if under rate limit - allow if we haven't hit the limit yet
        if len(current_messages) < self.messages_per_minute:
            self.client_messages[client_id].append(now)
            print("Rate limit check passed")
            return True
            
        print("Rate limit exceeded")
        return False
    
    def reset_for_client(self, client_id: str):
        """Reset rate limit for a specific client"""
        print(f"Resetting rate limit for client {client_id}")
        self.client_messages[client_id] = []
    
    def time_until_reset(self, client_id: str) -> float:
        """Get seconds until oldest message expires"""
        if not self.client_messages[client_id]:
            return 0
            
        now = time.time()
        oldest_message = min(self.client_messages[client_id])
        return max(0, (oldest_message + 60) - now) 