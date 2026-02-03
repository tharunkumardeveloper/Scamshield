from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from mangum import Mangum
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.request_models import HoneypotRequest
from models.response_models import HoneypotResponse
from agents.scam_detector import ScamDetector
from agents.persona_agent import PersonaAgent
from agents.intelligence_extractor import IntelligenceExtractor
from agents.engagement_tracker import EngagementTracker
from services.redis_service import RedisService
from services.supabase_service import SupabaseService
from utils.auth import verify_api_key
from datetime import datetime

app = FastAPI(title="ScamShield Honeypot API")

@app.get("/")
def root():
    return {
        "service": "ScamShield Honeypot API",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/honeypot")
async def honeypot_endpoint(
    request: HoneypotRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    if not verify_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Initialize on demand
        scam_detector = ScamDetector()
        persona_agent = PersonaAgent(api_key=os.getenv("GROQ_API_KEY"))
        intelligence_extractor = IntelligenceExtractor()
        engagement_tracker = EngagementTracker()
        
        scam_analysis = scam_detector.analyze(
            message=request.message,
            history=request.conversation_history
        )
        
        agent_response = await persona_agent.generate_response(
            message=request.message,
            conversation_id=request.conversation_id,
            history=request.conversation_history,
            scam_detected=scam_analysis["detected"]
        )
        
        extracted_intel = intelligence_extractor.extract(
            message=request.message,
            response=agent_response
        )
        
        metrics = engagement_tracker.calculate(
            conversation_id=request.conversation_id,
            history=request.conversation_history,
            new_turn={
                "scammer": request.message,
                "agent": agent_response
            }
        )
        
        return {
            "status": "success",
            "scam_detected": scam_analysis["detected"],
            "confidence_score": scam_analysis["confidence"],
            "scam_type": scam_analysis["scam_type"],
            "agent_response": agent_response,
            "conversation_turns": len(request.conversation_history) + 1,
            "extracted_intelligence": extracted_intel,
            "engagement_metrics": metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

handler = Mangum(app)
