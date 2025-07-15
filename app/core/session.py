import uuid
from typing import Dict, Any, List
from fastapi import WebSocket

class SessionManager:
    """Manages user sessions and their associated data"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    def create_session(self, websocket: WebSocket) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            "websocket": websocket,
            "data_profile": None,
            "dataframe": None,
            "conversation_history": [],
            "file_name": None,
            "retry_count": 0
        }
        return session_id
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session by ID"""
        return self.active_sessions.get(session_id)
    
    def end_session(self, session_id: str) -> None:
        """End a session and clean up resources"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def update_session_data(self, session_id: str, key: str, value: Any) -> None:
        """Update a specific data element in the session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id][key] = value
    
    def add_to_conversation(self, session_id: str, message: Dict[str, Any]) -> None:
        """Add a message to the conversation history"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["conversation_history"].append(message)
    
    def reset_retry_count(self, session_id: str) -> None:
        """Reset the retry counter for error handling"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["retry_count"] = 0
    
    def increment_retry_count(self, session_id: str) -> int:
        """Increment retry counter and return new value"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["retry_count"] += 1
            return self.active_sessions[session_id]["retry_count"]
        return 0