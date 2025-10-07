from typing import List, Dict, Any
import os
import sys
import time
import threading
from llama_cpp import Llama
from huggingface_hub import hf_hub_download, HfFileSystem
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def track_download_progress(cache_dir, repo_id, total_size_mb):
    """Track download progress by monitoring .incomplete file"""
    def monitor():
        count = 0
        while True:
            time.sleep(30)
            count += 1
            
            # Find .incomplete file
            incomplete_file = None
            blob_dir = os.path.join(cache_dir, f"models--{repo_id.replace('/', '--')}", "blobs")
            
            if os.path.exists(blob_dir):
                for file in os.listdir(blob_dir):
                    if file.endswith('.incomplete'):
                        incomplete_file = os.path.join(blob_dir, file)
                        break
            
            if incomplete_file and os.path.exists(incomplete_file):
                try:
                    current_size_mb = os.path.getsize(incomplete_file) / (1024 * 1024)
                    progress = (current_size_mb / total_size_mb) * 100
                    logger.info(f"📥 Download progress: {progress:.1f}% ({current_size_mb:.1f}/{total_size_mb:.1f} MB)")
                    sys.stdout.flush()
                except:
                    logger.info(f"🔄 Download in progress... ({count * 30}s elapsed)")
                    sys.stdout.flush()
            else:
                logger.info(f"🔄 Download in progress... ({count * 30}s elapsed)")
                sys.stdout.flush()
    
    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    return thread

class NLPService:
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            logger.info("🚀 Initializing NLP Service...")
            
            # Check if model already exists
            cache_dir = "./models"
            os.makedirs(cache_dir, exist_ok=True)
            
            repo_id = "mradermacher/natural-sql-7b-i1-GGUF"
            filename = "natural-sql-7b.i1-Q4_K_M.gguf"
            
            logger.info(f"📥 Model: {repo_id}")
            logger.info(f"📄 File: {filename}")
            
            # Get file size
            try:
                fs = HfFileSystem()
                file_info = fs.info(f"{repo_id}/{filename}")
                file_size_mb = file_info['size'] / (1024 * 1024)
                logger.info(f"📊 Model size: {file_size_mb:.1f} MB")
            except:
                file_size_mb = 4000
                logger.info("📊 Model size: ~4000 MB")
            
            logger.info("⬇️ Starting download (progress updates every 30s)...")
            sys.stdout.flush()
            
            # Start progress tracking
            progress_thread = track_download_progress(cache_dir, repo_id, file_size_mb)
            
            # Download model
            model_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                cache_dir=cache_dir,
                resume_download=True
            )
            
            logger.info(f"✅ Download completed: {model_path}")
            logger.info("🔄 Loading model into memory...")
            sys.stdout.flush()
            
            # Initialize Llama model with verbose output
            self.model = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=4,
                verbose=True  # Enable verbose output for loading progress
            )
            
            logger.info("🎉 Model loaded successfully!")
            logger.info("✨ Ready to convert natural language to SQL queries")
            sys.stdout.flush()
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            logger.error("🚫 Model loading failed")
            sys.stdout.flush()
            self.model = None

    def text_to_sql(self, text: str, schema: List[Dict], context: List[str] = None) -> str:
        if not self.model:
            raise Exception("Model not loaded. Cannot generate SQL without AI model.")
        
        # Build schema context
        schema_text = self._build_schema_context(schema)
        
        # Create prompt for the model
        prompt = f"""### Task
Generate a SQL query for the following request.

### Database Schema
{schema_text}

### Request
{text}

### SQL Query
"""
        
        # Generate SQL using the model
        response = self.model(
            prompt,
            max_tokens=256,
            temperature=0.1,
            stop=["\n\n", "###"],
            echo=False
        )
        
        sql = response['choices'][0]['text'].strip()
        
        # Clean up the SQL
        if sql.startswith('```sql'):
            sql = sql[6:]
        if sql.endswith('```'):
            sql = sql[:-3]

        return sql.strip()
    
    def _build_schema_context(self, schema: List[Dict]) -> str:
        schema_lines = []
        for table in schema:
            table_name = table['name']
            columns = []
            for col in table['columns']:
                col_def = f"{col['name']} {col['type']}"
                if col.get('primary_key'):
                    col_def += " PRIMARY KEY"
                columns.append(col_def)
            
            schema_lines.append(f"CREATE TABLE {table_name} (\n  {', '.join(columns)}\n);")
        
        return "\n\n".join(schema_lines)
    
    def format_error_with_query(self, error: str, generated_query: str, original_text: str) -> str:
        """Format error message with the generated query for user review"""
        return f"Query execution failed. Here's what I generated - can you check if this looks right?\n\nGenerated Query: {generated_query}\n\nOriginal Request: {original_text}\n\nError: {error}\n\nI'm not confident about this query. Please review and let me know if adjustments are needed."

    def get_explanation(self, sql: str, original_query: str) -> str:
        """Generate explanation for the SQL query"""
        return f"Generated SQL query for: '{original_query}'. The query retrieves data based on your natural language request."