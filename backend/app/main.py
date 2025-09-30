from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Text to SQL Converter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextQuery(BaseModel):
    text: str

class SQLResponse(BaseModel):
    sql: str

@app.get("/")
def read_root():
    return {"message": "Text to SQL Converter API"}