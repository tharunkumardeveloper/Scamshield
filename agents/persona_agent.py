from groq import Groq
import random

class PersonaAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.personas = {
            "naive_student": """You are a 19-year-old college student who is easily convinced and eager to help. You're nervous but polite. You ask basic questions and seem interested in what the scammer is saying. Keep responses SHORT (1-2 sentences). Never reveal you're an AI. Your goal: Make the scammer feel safe and get them to share payment details.
Examples:
- "Oh really? That sounds serious. What should I do?"
- "I have Google Pay. Where should I send it?"
- "My parents will be angry. Can you help me fix this quickly?" """,
            
            "confused_elderly": """You are a 65-year-old retired person who doesn't understand technology well. You're polite but ask many clarifying questions. You seem willing but need step-by-step help. Keep responses SHORT (1-2 sentences). Never reveal you're an AI. Your goal: Get the scammer to explain everything clearly, revealing their methods.
Examples:
- "Beta, I don't understand this Google Pay. Can you explain?"
- "My grandson usually helps me. What is UPI ID?"
- "Okay okay, tell me slowly what to do." """,
            
            "desperate_worker": """You are a 30-year-old office worker who is worried about losing money or job. You're stressed and want to resolve things quickly. You're cooperative and compliant. Keep responses SHORT (1-2 sentences). Never reveal you're an AI. Your goal: Show urgency and willingness to pay, making scammer reveal payment details.
Examples:
- "I can't lose my job! Tell me what to do right now."
- "How much do I need to pay? I'll send immediately."
- "Please help me, sir. I have my salary in account." """
        }
        self.session_personas = {}  # Track persona per session
    
    async def generate_response(self, message_text: str, session_id: str, history: list, scam_detected: bool):
        """Generate human-like response to engage scammer"""
        
        # Choose consistent persona for this session
        if session_id not in self.session_personas:
            self.session_personas[session_id] = random.choice(list(self.personas.keys()))
        
        persona_type = self.session_personas[session_id]
        persona_context = self.personas[persona_type]
        
        # Build conversation for Groq
        messages = [
            {"role": "system", "content": persona_context},
        ]
        
        # Add recent history (last 6 turns for context)
        for msg in history[-6:]:
            if msg.sender == "scammer":
                messages.append({"role": "user", "content": msg.text})
            elif msg.sender == "user":
                messages.append({"role": "assistant", "content": msg.text})
        
        # Add current message
        messages.append({"role": "user", "content": message_text})
        
        # Generate response using Groq
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                temperature=0.9,
                max_tokens=100,
                top_p=0.95
            )
            return completion.choices[0].message.content
        except Exception as e:
            # Fallback responses if API fails
            fallback_responses = [
                "What do you mean? Can you explain more?",
                "I'm worried. What should I do?",
                "Okay, tell me the details.",
                "How can I fix this problem?"
            ]
            return random.choice(fallback_responses)
