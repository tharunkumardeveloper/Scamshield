from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from models.request_models import HoneypotRequest, Message
from models.response_models import HoneypotResponse, ExtractedIntelligence
from agents.scam_detector import ScamDetector
from agents.persona_agent import PersonaAgent
from agents.intelligence_extractor import IntelligenceExtractor
from services.guvi_callback import GuviCallbackService
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ScamShield Honeypot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
scam_detector = ScamDetector()
persona_agent = PersonaAgent(api_key=os.getenv("GROQ_API_KEY", ""))
intelligence_extractor = IntelligenceExtractor()
guvi_callback = GuviCallbackService()

# Simple in-memory session tracking (for production, use Redis)
session_data = {}

@app.get("/")
async def root():
    return {
        "service": "ScamShield Honeypot API",
        "status": "active",
        "version": "2.0.0",
        "competition": "GUVI Agentic Honey-Pot Challenge"
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
    """
    Main honeypot endpoint - accepts scam messages and returns agent responses
    Format matches GUVI competition requirements
    """
    
    # Verify API key
    expected_key = os.getenv("API_KEY", "your-secret-key")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        session_id = request.sessionId
        current_message = request.message
        history = request.conversationHistory
        
        # Step 1: Detect scam intent
        scam_analysis = scam_detector.analyze(
            message_text=current_message.text,
            history=history
        )
        
        logger.info(f"Session {session_id}: Scam detected={scam_analysis['detected']}, confidence={scam_analysis['confidence']}")
        
        # Step 2: Generate persona response
        agent_reply = await persona_agent.generate_response(
            message_text=current_message.text,
            session_id=session_id,
            history=history,
            scam_detected=scam_analysis["detected"]
        )
        
        # Step 3: Update conversation history with agent's response
        updated_history = history + [
            current_message,
            Message(sender="user", text=agent_reply, timestamp=current_message.timestamp)
        ]
        
        # Step 4: Extract intelligence from full conversation
        extracted_intel = intelligence_extractor.extract(updated_history)
        
        # Step 5: Track session data
        if session_id not in session_data:
            session_data[session_id] = {
                "scam_detected": scam_analysis["detected"],
                "scam_type": scam_analysis.get("scam_type", "unknown"),
                "start_time": datetime.utcnow(),
                "message_count": 0
            }
        
        session_data[session_id]["message_count"] = len(updated_history)
        session_data[session_id]["last_intelligence"] = extracted_intel
        
        # Step 6: Check if conversation should end and send final callback
        should_end = guvi_callback.should_end_conversation(
            history_length=len(updated_history),
            intelligence=extracted_intel,
            scam_detected=scam_analysis["detected"]
        )
        
        if should_end and scam_analysis["detected"]:
            # Generate agent notes
            agent_notes = f"Scam type: {scam_analysis.get('scam_type', 'unknown')}. "
            agent_notes += f"Engagement: {len(updated_history)} messages exchanged. "
            
            if extracted_intel.upiIds:
                agent_notes += "Extracted UPI IDs. "
            if extracted_intel.bankAccounts:
                agent_notes += "Extracted bank accounts. "
            if extracted_intel.phishingLinks:
                agent_notes += "Detected phishing links. "
            
            agent_notes += "Scammer used urgency tactics and attempted to extract sensitive information."
            
            # Send final result to GUVI
            callback_success = await guvi_callback.send_final_result(
                session_id=session_id,
                scam_detected=True,
                total_messages=len(updated_history),
                intelligence=extracted_intel,
                agent_notes=agent_notes
            )
            
            logger.info(f"Session {session_id}: Final callback sent, success={callback_success}")
        
        # Return simple response format as per competition requirements
        return HoneypotResponse(
            status="success",
            reply=agent_reply
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# Vercel serverless handler
handler = Mangum(app)
