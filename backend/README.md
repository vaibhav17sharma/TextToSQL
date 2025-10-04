# Text-to-SQL Backend API

FastAPI backend for converting natural language queries to SQL.

## API Endpoints

### Database Connection
- `POST /api/connect-db` - Connect using credentials
- `POST /api/connect-db/file` - Connect using uploaded file
- `GET /api/connection/status` - Check connection status
- `POST /api/disconnect` - Disconnect from database

### Schema & Queries
- `GET /api/schema` - Get database schema
- `POST /api/query` - Execute natural language query

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Supported Databases
- PostgreSQL
- MySQL
- SQLite (file upload)

## Environment Variables
- `DATABASE_URL` - Default database connection string
- `DEBUG` - Enable debug mode