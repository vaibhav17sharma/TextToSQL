from typing import List, Dict, Any
import os
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_progress_callback(filename, current, total):
    """Callback to show download progress"""
    if total > 0:
        percent = (current / total) * 100
        logger.info(f"Downloading {filename}: {percent:.1f}% ({current:,}/{total:,} bytes)")

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
            
            logger.info("📥 Checking for model download...")
            logger.info("Model: mradermacher/natural-sql-7b-i1-GGUF")
            logger.info("This may take a few minutes on first run...")
            
            # Download model if not exists (with progress)
            model_path = hf_hub_download(
                repo_id="mradermacher/natural-sql-7b-i1-GGUF",
                filename="natural-sql-7b.i1-Q4_K_M.gguf",
                cache_dir=cache_dir,
                resume_download=True
            )
            
            logger.info(f"✅ Model downloaded to: {model_path}")
            logger.info("🔄 Loading model into memory...")
            
            # Initialize Llama model with verbose output
            self.model = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=4,
                verbose=True  # Enable verbose output for loading progress
            )
            
            logger.info("🎉 Model loaded successfully!")
            logger.info("Ready to convert natural language to SQL queries.")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            logger.info("🔄 Falling back to basic SQL generation...")
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