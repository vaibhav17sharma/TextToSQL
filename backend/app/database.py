import sqlite3
import time
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from .models import Table, Column

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.connection_info = None

    def connect_credentials(self, host: str, port: int, username: str, password: str, database: str, db_type: str = "postgresql") -> bool:
        try:
            if db_type == "postgresql":
                connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            elif db_type == "mysql":
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            else:
                raise ValueError("Unsupported database type")
            
            self.engine = create_engine(connection_string)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.connection_info = {"type": "credentials", "host": host, "database": database}
            return True
        except Exception as e:
            raise Exception(f"Connection failed: {str(e)}")

    def connect_sqlite(self, file_path: str) -> bool:
        try:
            connection_string = f"sqlite:///{file_path}"
            self.engine = create_engine(connection_string)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.connection_info = {"type": "file", "file": file_path}
            return True
        except Exception as e:
            raise Exception(f"SQLite connection failed: {str(e)}")

    def get_schema(self) -> List[Table]:
        if not self.engine:
            raise Exception("No database connection")
        
        try:
            inspector = inspect(self.engine)
            tables = []
            
            for table_name in inspector.get_table_names():
                columns = []
                table_columns = inspector.get_columns(table_name)
                pk_constraint = inspector.get_pk_constraint(table_name)
                fk_constraints = inspector.get_foreign_keys(table_name)
                
                primary_keys = pk_constraint.get('constrained_columns', [])
                
                for col in table_columns:
                    # Check for foreign keys
                    foreign_key = None
                    for fk in fk_constraints:
                        if col['name'] in fk['constrained_columns']:
                            ref_table = fk['referred_table']
                            ref_col = fk['referred_columns'][0]
                            foreign_key = f"{ref_table}.{ref_col}"
                            break
                    
                    columns.append(Column(
                        name=col['name'],
                        type=str(col['type']),
                        primary_key=col['name'] in primary_keys,
                        foreign_key=foreign_key
                    ))
                
                tables.append(Table(name=table_name, columns=columns))
            
            return tables
        except Exception as e:
            raise Exception(f"Failed to get schema: {str(e)}")

    def execute_query(self, sql: str) -> Dict[str, Any]:
        if not self.engine:
            raise Exception("No database connection")
        
        try:
            start_time = time.time()
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                columns = result.keys()
                
                # Convert to list of dictionaries
                results = [dict(zip(columns, row)) for row in rows]
            
            execution_time = time.time() - start_time
            
            return {
                "sql": sql,
                "results": results,
                "execution_time": round(execution_time, 3)
            }
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")

    def disconnect(self):
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.connection_info = None

    def is_connected(self) -> bool:
        return self.engine is not None