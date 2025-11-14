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
    QueryRequest, QueryResponse, ErrorResponse, QuerySubmitResponse, QueryStatusResponse,
    SystemStats, ContextLoadResponse
)
from .database import DatabaseManager
from .nlp_service import NLPService
from .session_manager import SessionManager
from .query_queue import QueryQueue, QueryStatus



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
    
    # Start background tasks
    cleanup_task = asyncio.create_task(session_cleanup_task())
    queue_processor_task = asyncio.create_task(query_processor_task())
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    queue_processor_task.cancel()
    logger.info("Shutting down Text to SQL Converter API...")

app = FastAPI(title="Text to SQL Converter API", lifespan=lifespan)

async def session_cleanup_task():
    """Background task to clean up expired sessions every 5 minutes"""
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            session_manager.cleanup_expired_sessions()
            query_queue.cleanup_old_queries()
            logger.info(f"Session cleanup completed. Active sessions: {session_manager.get_session_count()}")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in session cleanup: {e}")

async def query_processor_task():
    """Background task to process queued queries"""
    while True:
        try:
            query_id = await query_queue.get_next_query()
            if query_id:
                await process_query(query_id)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in query processor: {e}")

async def process_query(query_id: str):
    """Process a single query from the queue"""
    queued_query = query_queue.get_query_status(query_id)
    if not queued_query:
        return
    
    query_queue.update_query_status(query_id, QueryStatus.PROCESSING)
    
    try:
        db_manager = session_manager.get_session(queued_query.session_id)
        if not db_manager or not db_manager.is_connected():
            raise Exception("No database connection for session")
        
        # Process query asynchronously
        def process_nlp_query():
            schema = db_manager.get_schema()
            schema_dict = [table.dict() for table in schema]
            sql = nlp_service.text_to_sql(queued_query.query, schema_dict, queued_query.context)
            result = db_manager.execute_query(sql)
            explanation = nlp_service.get_explanation(sql, queued_query.query)
            return {
                "sql": result["sql"],
                "results": result["results"],
                "execution_time": result["execution_time"],
                "explanation": explanation
            }
        
        query_result = await asyncio.get_event_loop().run_in_executor(None, process_nlp_query)
        query_queue.update_query_status(query_id, QueryStatus.COMPLETED, result=query_result)
        
    except Exception as e:
        error_message = nlp_service.format_error_with_query(str(e), "", queued_query.query) if hasattr(nlp_service, 'format_error_with_query') else str(e)
        query_queue.update_query_status(query_id, QueryStatus.FAILED, error=error_message)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
session_manager = SessionManager()
nlp_service = NLPService()
query_queue = QueryQueue()

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
async def get_schema(session_id: str = Header(..., alias="X-Session-ID")):
    try:
        db_manager = session_manager.get_session(session_id)
        if not db_manager or not db_manager.is_connected():
            raise HTTPException(status_code=400, detail="No database connection for session")
        
        tables = db_manager.get_schema()
        return SchemaResponse(tables=tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schema/refresh", response_model=SchemaResponse)
async def refresh_schema(session_id: str = Header(..., alias="X-Session-ID")):
    try:
        db_manager = session_manager.get_session(session_id)
        if not db_manager or not db_manager.is_connected():
            raise HTTPException(status_code=400, detail="No database connection for session")
        
        tables = db_manager.get_schema()
        return SchemaResponse(tables=tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query", response_model=QuerySubmitResponse)
async def submit_query(request: QueryRequest):
    try:
        # Validate session exists
        db_manager = session_manager.get_session(request.session_id)
        if not db_manager or not db_manager.is_connected():
            raise HTTPException(status_code=400, detail="No database connection for session")
        
        # Add query to queue
        query_id = await query_queue.add_query(request.session_id, request.query, request.context)
        
        return QuerySubmitResponse(
            query_id=query_id,
            status="queued",
            message="Query added to processing queue"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/query/{query_id}/status", response_model=QueryStatusResponse)
async def get_query_status(query_id: str):
    try:
        queued_query = query_queue.get_query_status(query_id)
        if not queued_query:
            raise HTTPException(status_code=404, detail="Query not found")
        
        result = None
        if queued_query.status == QueryStatus.COMPLETED and queued_query.result:
            result = QueryResponse(**queued_query.result)
        
        # Include system stats in response
        stats = get_system_stats()
        
        return QueryStatusResponse(
            query_id=query_id,
            status=queued_query.status.value,
            result=result,
            error=queued_query.error,
            created_at=queued_query.created_at.isoformat(),
            stats=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/connection/status")
async def connection_status(session_id: str = Header(..., alias="X-Session-ID")):
    db_manager = session_manager.get_session(session_id)
    if not db_manager:
        return {"connected": False, "connection_info": None}
    
    return {
        "connected": db_manager.is_connected(),
        "connection_info": db_manager.connection_info
    }

@app.post("/api/disconnect")
async def disconnect(session_id: str = Header(..., alias="X-Session-ID")):
    try:
        session_manager.cleanup_session(session_id)
        # Clear context when disconnecting
        nlp_service.context_loaded = False
        nlp_service.loaded_schema = None
        return {"success": True, "message": "Disconnected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_system_stats() -> SystemStats:
    """Get current system statistics"""
    total_queries = len(query_queue.queries)
    queued = sum(1 for q in query_queue.queries.values() if q.status == QueryStatus.QUEUED)
    processing = sum(1 for q in query_queue.queries.values() if q.status == QueryStatus.PROCESSING)
    completed = sum(1 for q in query_queue.queries.values() if q.status == QueryStatus.COMPLETED)
    failed = sum(1 for q in query_queue.queries.values() if q.status == QueryStatus.FAILED)
    
    return SystemStats(
        active_sessions=session_manager.get_session_count(),
        total_queries=total_queries,
        queued=queued,
        processing=processing,
        completed=completed,
        failed=failed,
        queue_size=query_queue.queue.qsize()
    )

@app.get("/api/system/stats", response_model=SystemStats)
async def get_stats():
    """Get current system statistics - lightweight endpoint"""
    return get_system_stats()

@app.post("/api/sessions/cleanup")
async def cleanup_expired_sessions():
    """Manually trigger cleanup of expired sessions"""
    session_manager.cleanup_expired_sessions()
    return {
        "success": True,
        "stats": get_system_stats(),
        "message": "Expired sessions cleaned up"
    }

@app.post("/api/context/load", response_model=ContextLoadResponse)
async def load_context(session_id: str = Header(..., alias="X-Session-ID")):
    """Load database schema context to the model and execute sample queries"""
    try:
        db_manager = session_manager.get_session(session_id)
        if not db_manager or not db_manager.is_connected():
            raise HTTPException(status_code=400, detail="No database connection for session")
        
        # Get schema
        schema = db_manager.get_schema()
        if not schema:
            raise HTTPException(status_code=400, detail="No tables found in database")
        
        # Load context and test query asynchronously
        async def load_and_test():
            # Load context to NLP service
            context_loaded = nlp_service.load_context(schema)
            if not context_loaded:
                raise Exception("Failed to load context to AI model")
            
            # Test with NLP query for first table
            if schema:
                first_table = schema[0]
                nlp_query = f"Select 1 row of the {first_table.name}"
                schema_dict = [table.dict() for table in schema]
                generated_sql = nlp_service.text_to_sql(nlp_query, schema_dict)
                db_manager.execute_query(generated_sql)
            
            return True
        
        # Execute asynchronously
        await asyncio.get_event_loop().run_in_executor(None, load_and_test)
        
        return ContextLoadResponse(
            success=True,
            message="Context loaded successfully",
            tables_count=len(schema),
            sample_results=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/context/status")
async def get_context_status(session_id: str = Header(..., alias="X-Session-ID")):
    """Get context loading status"""
    return {
        "loaded": nlp_service.is_context_loaded(),
        "message": "Context loaded" if nlp_service.is_context_loaded() else "Context not loaded"
    }