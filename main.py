from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from models.request_models import HoneypotRequest
from models.response_models import HoneypotResponse
from agents.scam_detector import ScamDetector
from agents.persona_agent import PersonaAgent
from agents.intelligence_extractor import IntelligenceExtractor
from agents.engagement_tracker import EngagementTracker
from services.redis_service import RedisService
from services.supabase_service import SupabaseService
from utils.auth import verify_api_key
import os
from datetime import datetime

app = FastAPI(title="ScamShield Honeypot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check required environment variables
required_vars = ["GROQ_API_KEY", "UPSTASH_REDIS_URL", "SUPABASE_URL", "SUPABASE_KEY", "API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
    # Don't raise error, let it fail gracefully

# Initialize services
try:
    redis_service = RedisService(os.getenv("UPSTASH_REDIS_URL"))
    supabase_service = SupabaseService(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    
    # Initialize agents
    scam_detector = ScamDetector()
    persona_agent = PersonaAgent(api_key=os.getenv("GROQ_API_KEY"))
    intelligence_extractor = IntelligenceExtractor()
    engagement_tracker = EngagementTracker()
except Exception as e:
    print(f"Initialization error: {str(e)}")
    # Services will be None, endpoints will handle gracefully

@app.get("/")
async def root():
    return {
        "service": "ScamShield Honeypot API",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    request: HoneypotRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    # Verify API key
    if not verify_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Step 1: Detect scam intent
        scam_analysis = scam_detector.analyze(
            message=request.message,
            history=request.conversation_history
        )
        
        # Step 2: Generate persona response
        agent_response = await persona_agent.generate_response(
            message=request.message,
            conversation_id=request.conversation_id,
            history=request.conversation_history,
            scam_detected=scam_analysis["detected"]
        )
        
        # Step 3: Extract intelligence
        extracted_intel = intelligence_extractor.extract(
            message=request.message,
            response=agent_response
        )
        
        # Step 4: Track engagement metrics
        metrics = engagement_tracker.calculate(
            conversation_id=request.conversation_id,
            history=request.conversation_history,
            new_turn={
                "scammer": request.message,
                "agent": agent_response
            }
        )
        
        # Step 5: Store in database
        await supabase_service.store_conversation(
            conversation_id=request.conversation_id,
            scam_analysis=scam_analysis,
            intelligence=extracted_intel,
            metrics=metrics
        )
        
        # Step 6: Update Redis state
        await redis_service.update_conversation(
            conversation_id=request.conversation_id,
            message=request.message,
            response=agent_response
        )
        
        # Return response
        return HoneypotResponse(
            status="success",
            scam_detected=scam_analysis["detected"],
            confidence_score=scam_analysis["confidence"],
            scam_type=scam_analysis["scam_type"],
            agent_response=agent_response,
            conversation_turns=len(request.conversation_history) + 1,
            extracted_intelligence=extracted_intel,
            engagement_metrics=metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


# Vercel serverless handler
handler = Mangum(app)


# Vercel serverless handler
handler = Mangum(app)
