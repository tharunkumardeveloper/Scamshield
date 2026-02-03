from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ConversationTurn(BaseModel):
    role: str
    content: str
    timestamp: str

class HoneypotRequest(BaseModel):
    conversation_id: str
    message: str
    conversation_history: List[ConversationTurn] = []
