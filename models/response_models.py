from pydantic import BaseModel
from typing import List, Dict

class ExtractedIntelligence(BaseModel):
    upi_ids: List[str] = []
    phone_numbers: List[str] = []
    bank_accounts: List[str] = []
    phishing_urls: List[str] = []
    keywords: List[str] = []

class EngagementMetrics(BaseModel):
    conversation_duration_seconds: int
    scammer_engagement_level: str
    intelligence_quality: str

class HoneypotResponse(BaseModel):
    status: str
    scam_detected: bool
    confidence_score: float
    scam_type: str
    agent_response: str
    conversation_turns: int
    extracted_intelligence: ExtractedIntelligence
    engagement_metrics: EngagementMetrics
