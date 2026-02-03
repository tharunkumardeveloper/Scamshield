from datetime import datetime

class EngagementTracker:
    def calculate(self, conversation_id: str, history: list, new_turn: dict):
        # Calculate conversation duration (mock - in real scenario use timestamps)
        duration = len(history) * 15  # Assume 15 seconds per turn
        
        # Determine engagement level
        engagement_level = "low"
        if len(history) >= 3:
            engagement_level = "medium"
        if len(history) >= 5:
            engagement_level = "high"
        
        # Determine intelligence quality
        intel_quality = "low"
        # Check if recent messages contain valuable patterns
        recent_text = " ".join([turn.content for turn in history[-3:]])
        if "@" in recent_text or "http" in recent_text:
            intel_quality = "medium"
        if len([t for t in history if "@" in t.content]) >= 2:
            intel_quality = "high"
        
        return {
            "conversation_duration_seconds": duration,
            "scammer_engagement_level": engagement_level,
            "intelligence_quality": intel_quality
        }
