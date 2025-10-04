# Text to SQL Converter

AI/ML powered application that converts natural language text to SQL queries.

## Tech Stack

- **Frontend**: React
- **Backend**: FastAPI
- **Database**: MySQL & PostgreSQL
- **AI/ML**: Natural language processing for SQL generation
- **Model**: mradermacher/natural-sql-7b-i1-GGUF

## Features

- Convert plain English to SQL queries
- Real-time query generation
- Clean, intuitive interface
- Multi-database support

## Quick Start with Docker

```bash
# Start all services with docker-compose
docker-compose up --build
```

Access the application at http://localhost:3000

## Architecture

- **Frontend**: React app served on port 3000 (exposed to host)
- **Backend**: FastAPI on internal network only
- **Databases**: PostgreSQL on internal network for testing purpose only not the Primary DB
- All services communicate through `texttosql-network`
