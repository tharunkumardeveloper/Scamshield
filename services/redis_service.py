import redis
import json
from datetime import datetime
import os

class RedisService:
    def __init__(self, url: str = None):
        if not url:
            url = os.getenv("UPSTASH_REDIS_URL")
        
        if not url:
            raise ValueError("UPSTASH_REDIS_URL environment variable is not set")
        
        self.client = redis.from_url(url, decode_responses=True)
    
    async def update_conversation(self, conversation_id: str, message: str, response: str):
        key = f"conv:{conversation_id}"
        
        # Get existing conversation
        existing = self.client.get(key)
        if existing:
            conv_data = json.loads(existing)
        else:
            conv_data = {"turns": []}
        
        # Add new turn
        conv_data["turns"].append({
            "scammer": message,
            "agent": response,
            "timestamp": str(datetime.utcnow())
        })
        
        # Store back
        self.client.setex(key, 86400, json.dumps(conv_data))  # 24 hour expiry
