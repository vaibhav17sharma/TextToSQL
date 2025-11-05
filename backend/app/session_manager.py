import uuid
import time
from typing import Dict, Optional
from .database import DatabaseManager

class SessionManager:
    def __init__(self, session_timeout: int = 3600):  # 1 hour timeout
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = session_timeout
    
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'db_manager': DatabaseManager(),
            'created_at': time.time(),
            'last_accessed': time.time()
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[DatabaseManager]:
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session expired
        if time.time() - session['last_accessed'] > self.session_timeout:
            self.cleanup_session(session_id)
            return None
        
        # Update last accessed time
        session['last_accessed'] = time.time()
        return session['db_manager']
    
    def cleanup_session(self, session_id: str):
        if session_id in self.sessions:
            # Disconnect database if connected
            db_manager = self.sessions[session_id]['db_manager']
            if db_manager.is_connected():
                db_manager.disconnect()
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        current_time = time.time()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if current_time - session['last_accessed'] > self.session_timeout
        ]
        for session_id in expired_sessions:
            self.cleanup_session(session_id)
    
    def get_session_count(self) -> int:
        return len(self.sessions)