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

class DownloadTracker:
    def __init__(self):
        self.stop_tracking = False
    
    def track_download_progress(self, cache_dir, repo_id, total_size_mb):
        """Track download progress by monitoring .incomplete file"""
        def monitor():
            count = 0
            while not self.stop_tracking:
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
                    # No incomplete file found, download might be complete
                    if count > 1:  # Only log if we've been tracking for a while
                        logger.info(f"🔄 Download in progress... ({count * 30}s elapsed)")
                        sys.stdout.flush()
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        self.stop_tracking = True

class NLPService:
    def __init__(self):
        self.model = None
        self.download_tracker = None
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
            
            # Check if model already exists locally
            expected_path = os.path.join(cache_dir, f"models--{repo_id.replace('/', '--')}", "snapshots")
            model_exists = False
            
            if os.path.exists(expected_path):
                for snapshot_dir in os.listdir(expected_path):
                    snapshot_path = os.path.join(expected_path, snapshot_dir, filename)
                    if os.path.exists(snapshot_path):
                        model_exists = True
                        model_path = snapshot_path
                        logger.info(f"✅ Model already downloaded: {model_path}")
                        break
            
            if not model_exists:
                logger.info("⬇️ Starting download (progress updates every 30s)...")
                sys.stdout.flush()
                
                # Start progress tracking
                self.download_tracker = DownloadTracker()
                progress_thread = self.download_tracker.track_download_progress(cache_dir, repo_id, file_size_mb)
                
                # Download model
                model_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    cache_dir=cache_dir,
                    resume_download=True
                )
                
                # Stop progress tracking
                if self.download_tracker:
                    self.download_tracker.stop()
                
                logger.info(f"✅ Download completed: {model_path}")
            else:
                logger.info("📁 Using existing model file")
            logger.info("🔄 Loading model into memory...")
            sys.stdout.flush()
            
            # Initialize Llama model with GPU acceleration if available
            gpu_available = self._check_gpu_available()
            
            if gpu_available:
                try:
                    logger.info("🚀 Attempting GPU acceleration...")
                    self.model = Llama(
                        model_path=model_path,
                        n_ctx=2048,
                        n_gpu_layers=-1,  # Use all GPU layers
                        verbose=False
                    )
                    logger.info("✨ Model loaded with GPU acceleration")
                except Exception as gpu_error:
                    logger.info(f"⚠️ GPU failed: {str(gpu_error)[:100]}...")
                    logger.info("🔄 Falling back to CPU...")
                    self._load_cpu_model(model_path)
            else:
                logger.info("💻 Loading model on CPU...")
                self._load_cpu_model(model_path)
            
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

    def _check_gpu_available(self) -> bool:
        """Check if GPU is available for llama-cpp-python"""
        logger.info("🔍 Checking GPU availability...")
        
        # Check NVIDIA runtime
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("✅ nvidia-smi detected")
                gpu_detected = True
            else:
                logger.info("❌ nvidia-smi failed")
                gpu_detected = False
        except:
            logger.info("❌ nvidia-smi not available")
            gpu_detected = False
        
        # Check llama-cpp-python GPU support
        try:
            from llama_cpp import llama_cpp_lib
            gpu_support = hasattr(llama_cpp_lib, 'llama_supports_gpu_offload') and llama_cpp_lib.llama_supports_gpu_offload()
            logger.info(f"🔧 llama-cpp GPU support: {gpu_support}")
        except Exception as e:
            logger.info(f"❌ llama-cpp GPU check failed: {e}")
            gpu_support = False
        
        # Check environment variables
        cuda_visible = os.environ.get('NVIDIA_VISIBLE_DEVICES', 'none')
        logger.info(f"🌍 NVIDIA_VISIBLE_DEVICES: {cuda_visible}")
        
        final_result = gpu_detected and gpu_support
        logger.info(f"🎯 Final GPU availability: {final_result}")
        return final_result
    
    def _load_cpu_model(self, model_path: str):
        """Load model on CPU"""
        self.model = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )
        logger.info("💻 Model loaded on CPU")

    def get_explanation(self, sql: str, original_query: str) -> str:
        """Generate explanation for the SQL query"""
        return f"Generated SQL query for: '{original_query}'. The query retrieves data based on your natural language request."