import requests
from models.response_models import FinalResultPayload, ExtractedIntelligence
import logging

logger = logging.getLogger(__name__)

class GuviCallbackService:
    """Service to send final results to GUVI evaluation endpoint"""
    
    CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    @staticmethod
    async def send_final_result(
        session_id: str,
        scam_detected: bool,
        total_messages: int,
        intelligence: ExtractedIntelligence,
        agent_notes: str
    ) -> bool:
        """
        Send final extracted intelligence to GUVI endpoint
        Returns True if successful, False otherwise
        """
        payload = {
            "sessionId": session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": {
                "bankAccounts": intelligence.bankAccounts,
                "upiIds": intelligence.upiIds,
                "phishingLinks": intelligence.phishingLinks,
                "phoneNumbers": intelligence.phoneNumbers,
                "suspiciousKeywords": intelligence.suspiciousKeywords
            },
            "agentNotes": agent_notes
        }
        
        try:
            response = requests.post(
                GuviCallbackService.CALLBACK_URL,
                json=payload,
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully sent final result for session {session_id}")
                return True
            else:
                logger.error(f"Failed to send final result: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending final result to GUVI: {str(e)}")
            return False
    
    @staticmethod
    def should_end_conversation(
        history_length: int,
        intelligence: ExtractedIntelligence,
        scam_detected: bool
    ) -> bool:
        """
        Determine if conversation should end and final callback should be sent
        
        Criteria:
        - Scam detected AND
        - Either: sufficient intelligence gathered OR conversation is long enough
        """
        if not scam_detected:
            return False
        
        # Check if we have valuable intelligence
        has_intelligence = (
            len(intelligence.bankAccounts) > 0 or
            len(intelligence.upiIds) > 0 or
            len(intelligence.phishingLinks) > 0 or
            len(intelligence.phoneNumbers) > 0
        )
        
        # End if we have intelligence and at least 5 turns
        if has_intelligence and history_length >= 5:
            return True
        
        # End if conversation is very long (10+ turns) even without much intelligence
        if history_length >= 10:
            return True
        
        return False
