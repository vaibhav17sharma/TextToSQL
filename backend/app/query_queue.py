import asyncio
import uuid
from typing import Dict, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class QueryStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class QueuedQuery:
    id: str
    session_id: str
    query: str
    context: list
    status: QueryStatus
    created_at: datetime
    result: Optional[dict] = None
    error: Optional[str] = None

class QueryQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.queries: Dict[str, QueuedQuery] = {}
        self.processing = False
    
    async def add_query(self, session_id: str, query: str, context: list = None) -> str:
        query_id = str(uuid.uuid4())
        queued_query = QueuedQuery(
            id=query_id,
            session_id=session_id,
            query=query,
            context=context or [],
            status=QueryStatus.QUEUED,
            created_at=datetime.now()
        )
        
        self.queries[query_id] = queued_query
        await self.queue.put(query_id)
        return query_id
    
    def get_query_status(self, query_id: str) -> Optional[QueuedQuery]:
        return self.queries.get(query_id)
    
    async def get_next_query(self) -> Optional[str]:
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None
    
    def update_query_status(self, query_id: str, status: QueryStatus, result: dict = None, error: str = None):
        if query_id in self.queries:
            self.queries[query_id].status = status
            if result:
                self.queries[query_id].result = result
            if error:
                self.queries[query_id].error = error
    
    def cleanup_old_queries(self, max_age_hours: int = 24):
        cutoff = datetime.now().timestamp() - (max_age_hours * 3600)
        to_remove = [
            qid for qid, query in self.queries.items()
            if query.created_at.timestamp() < cutoff
        ]
        for qid in to_remove:
            del self.queries[qid]