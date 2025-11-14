from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from enum import Enum

class DatabaseCredentials(BaseModel):
    type: str  # "credentials" or "file"
    db_type: Optional[str] = "postgresql"  # "postgresql" or "mysql"
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None

class ConnectionResponse(BaseModel):
    success: bool
    message: str
    connection_id: Optional[str] = None
    session_id: Optional[str] = None

class Column(BaseModel):
    name: str
    type: str
    primary_key: Optional[bool] = False
    foreign_key: Optional[str] = None

class Table(BaseModel):
    name: str
    columns: List[Column]

class SchemaResponse(BaseModel):
    tables: List[Table]

class QueryRequest(BaseModel):
    query: str
    context: Optional[List[str]] = []
    session_id: str

class QueryResponse(BaseModel):
    sql: str
    results: List[Dict[str, Any]]
    execution_time: float
    explanation: Optional[str] = None

class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    code: Optional[str] = None

class QuerySubmitResponse(BaseModel):
    query_id: str
    status: str
    message: str

class SystemStats(BaseModel):
    active_sessions: int
    total_queries: int
    queued: int
    processing: int
    completed: int
    failed: int
    queue_size: int

class QueryStatusResponse(BaseModel):
    query_id: str
    status: str
    result: Optional[QueryResponse] = None
    error: Optional[str] = None
    created_at: str
    stats: Optional[SystemStats] = None

class ContextLoadResponse(BaseModel):
    success: bool
    message: str
    tables_count: int
    sample_results: List[Dict[str, Any]]