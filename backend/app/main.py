from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import logging
from .models import (
    DatabaseCredentials, ConnectionResponse, SchemaResponse, 
    QueryRequest, QueryResponse, ErrorResponse
)
from .database import DatabaseManager
from .nlp_service import NLPService

app = FastAPI(title="Text to SQL Converter API")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Text to SQL Converter API...")
    logger.info("Initializing database manager...")
    logger.info("Initializing NLP service (this may take a few minutes on first run)...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db_manager = DatabaseManager()
nlp_service = NLPService()

@app.get("/")
def read_root():
    return {"message": "Text to SQL Converter API"}

@app.post("/api/connect-db", response_model=ConnectionResponse)
async def connect_database(credentials: DatabaseCredentials):
    try:
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
                connection_id="conn_123"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/connect-db/file", response_model=ConnectionResponse)
async def connect_database_file(file: UploadFile = File(...)):
    try:
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
                connection_id="conn_file_123"
            )
    except Exception as e:
        # Clean up temp file on error
        if 'tmp_file_path' in locals():
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/schema", response_model=SchemaResponse)
def get_schema():
    try:
        if not db_manager.is_connected():
            raise HTTPException(status_code=400, detail="No database connection")
        
        tables = db_manager.get_schema()
        return SchemaResponse(tables=tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schema/refresh", response_model=SchemaResponse)
def refresh_schema():
    try:
        if not db_manager.is_connected():
            raise HTTPException(status_code=400, detail="No database connection")
        
        tables = db_manager.get_schema()
        return SchemaResponse(tables=tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query", response_model=QueryResponse)
def execute_query(request: QueryRequest):
    try:
        if not db_manager.is_connected():
            raise HTTPException(status_code=400, detail="No database connection")
        
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
def connection_status():
    return {
        "connected": db_manager.is_connected(),
        "connection_info": db_manager.connection_info
    }

@app.post("/api/disconnect")
def disconnect():
    try:
        db_manager.disconnect()
        return {"success": True, "message": "Disconnected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))