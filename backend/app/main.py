from fastapi import FastAPI, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import logging
import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from .models import (
    DatabaseCredentials, ConnectionResponse, SchemaResponse, 
    QueryRequest, QueryResponse, ErrorResponse
)
from .database import DatabaseManager
from .nlp_service import NLPService
from .session_manager import SessionManager



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Text to SQL Converter API...")
    logger.info("Initializing session manager...")
    logger.info("Initializing NLP service (this may take a few minutes on first run)...")
    
    # Start background task for session cleanup
    cleanup_task = asyncio.create_task(session_cleanup_task())
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    logger.info("Shutting down Text to SQL Converter API...")

app = FastAPI(title="Text to SQL Converter API", lifespan=lifespan)

async def session_cleanup_task():
    """Background task to clean up expired sessions every 5 minutes"""
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            session_manager.cleanup_expired_sessions()
            logger.info(f"Session cleanup completed. Active sessions: {session_manager.get_session_count()}")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in session cleanup: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
session_manager = SessionManager()
nlp_service = NLPService()

@app.get("/")
def read_root():
    return {"message": "Text to SQL Converter API"}

@app.post("/api/connect-db", response_model=ConnectionResponse)
async def connect_database(credentials: DatabaseCredentials):
    try:
        # Create new session
        session_id = session_manager.create_session()
        db_manager = session_manager.get_session(session_id)
        
        if credentials.type == "credentials":
            success = db_manager.connect_credentials(
                host=credentials.host,
                port=credentials.port,
                username=credentials.username,
                password=credentials.password,
                database=credentials.database,
                db_type=credentials.db_type
            )
        else:
            raise HTTPException(status_code=400, detail="File upload not implemented in this endpoint")
        
        if success:
            return ConnectionResponse(
                success=True,
                message="Connected successfully",
                connection_id=f"conn_{session_id[:8]}",
                session_id=session_id
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/connect-db/file", response_model=ConnectionResponse)
async def connect_database_file(file: UploadFile = File(...)):
    try:
        # Create new session
        session_id = session_manager.create_session()
        db_manager = session_manager.get_session(session_id)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        success = db_manager.connect_sqlite(tmp_file_path)
        
        if success:
            return ConnectionResponse(
                success=True,
                message="Connected successfully",
                connection_id=f"conn_file_{session_id[:8]}",
                session_id=session_id
            )
    except Exception as e:
        # Clean up temp file on error
        if 'tmp_file_path' in locals():
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/schema", response_model=SchemaResponse)
def get_schema(session_id: str = Header(..., alias="X-Session-ID")):
    try:
        db_manager = session_manager.get_session(session_id)
        if not db_manager or not db_manager.is_connected():
            raise HTTPException(status_code=400, detail="No database connection for session")
        
        tables = db_manager.get_schema()
        return SchemaResponse(tables=tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schema/refresh", response_model=SchemaResponse)
def refresh_schema(session_id: str = Header(..., alias="X-Session-ID")):
    try:
        db_manager = session_manager.get_session(session_id)
        if not db_manager or not db_manager.is_connected():
            raise HTTPException(status_code=400, detail="No database connection for session")
        
        tables = db_manager.get_schema()
        return SchemaResponse(tables=tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query", response_model=QueryResponse)
def execute_query(request: QueryRequest):
    try:
        db_manager = session_manager.get_session(request.session_id)
        if not db_manager or not db_manager.is_connected():
            raise HTTPException(status_code=400, detail="No database connection for session")
        
        # Get schema for context
        schema = db_manager.get_schema()
        schema_dict = [table.dict() for table in schema]
        
        # Convert natural language to SQL
        sql = nlp_service.text_to_sql(request.query, schema_dict, request.context)
        
        try:
            # Execute the query
            result = db_manager.execute_query(sql)
            
            # Get explanation
            explanation = nlp_service.get_explanation(sql, request.query)
            
            return QueryResponse(
                sql=result["sql"],
                results=result["results"],
                execution_time=result["execution_time"],
                explanation=explanation
            )
        except Exception as exec_error:
            # Query execution failed - show the generated query for review
            error_message = nlp_service.format_error_with_query(
                str(exec_error), sql, request.query
            )
            raise HTTPException(status_code=400, detail=error_message)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/connection/status")
def connection_status(session_id: str = Header(..., alias="X-Session-ID")):
    db_manager = session_manager.get_session(session_id)
    if not db_manager:
        return {"connected": False, "connection_info": None}
    
    return {
        "connected": db_manager.is_connected(),
        "connection_info": db_manager.connection_info
    }

@app.post("/api/disconnect")
def disconnect(session_id: str = Header(..., alias="X-Session-ID")):
    try:
        session_manager.cleanup_session(session_id)
        return {"success": True, "message": "Disconnected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/stats")
def get_session_stats():
    """Get current session statistics"""
    return {
        "active_sessions": session_manager.get_session_count(),
        "message": "Session statistics"
    }

@app.post("/api/sessions/cleanup")
def cleanup_expired_sessions():
    """Manually trigger cleanup of expired sessions"""
    session_manager.cleanup_expired_sessions()
    return {
        "success": True,
        "active_sessions": session_manager.get_session_count(),
        "message": "Expired sessions cleaned up"
    }