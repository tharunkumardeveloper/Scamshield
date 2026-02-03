from supabase import create_client, Client
from datetime import datetime

class SupabaseService:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
    
    async def store_conversation(self, conversation_id: str, scam_analysis: dict, intelligence: dict, metrics: dict):
        data = {
            "conversation_id": conversation_id,
            "scam_detected": scam_analysis["detected"],
            "confidence_score": scam_analysis["confidence"],
            "scam_type": scam_analysis["scam_type"],
            "extracted_intelligence": intelligence,
            "engagement_metrics": metrics,
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            self.client.table("honeypot_conversations").insert(data).execute()
        except Exception as e:
            print(f"Database error: {str(e)}")
