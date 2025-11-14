# Text to SQL Converter

AI/ML powered application that converts natural language text to SQL queries.

## 📸 Screenshots

![Landing Page](./demo/images/landing.avif)
*Welcome to Text to SQL Converter*

![Main Interface](./demo/images/main-interface.avif)
*Convert natural language to SQL queries with ease*

![Database Schema](./demo/images/schema.avif)
*Database schema visualization*

![Query Results](./demo/images/query-result.avif)
*Real-time SQL generation and execution*

![Session Management](./demo/images/session.avif)
*Manage your query sessions*

## 🎥 Demo Video

[![Demo Video](https://img.youtube.com/vi/AtDVDImZVpU/0.jpg)](https://youtu.be/AtDVDImZVpU)

*Watch the Text to SQL converter in action*

## Tech Stack

- **Frontend**: React
- **Backend**: FastAPI
- **Database**: MySQL & PostgreSQL
- **AI/ML**: Natural language processing for SQL generation
- **Model**: mradermacher/natural-sql-7b-i1-GGUF

## ✨ Features

- Convert plain English to SQL queries
- Real-time query generation
- Clean, intuitive interface
- Multi-database support

## 🚀 Deployment

### Quick Start

#### Development
```bash
# Start development environment
docker-compose up --build
```

#### Production
```bash
# Run deployment script (recommended)
./deploy.sh

# Or use make commands
make prod  # Docker deployment
make pm2-start  # PM2 deployment
```

Access the application at http://localhost:3000

### Deployment Options

#### 🐳 Docker (Recommended)
**Advantages:** Isolated environment, easy scaling, includes database

```bash
# Production
make prod

# View logs
make logs

# Stop services
make stop
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:3000/api (via Nginx proxy)
- Database: PostgreSQL (internal network)

#### ⚡ PM2 Process Manager
**Advantages:** Process management, auto-restart, load balancing

```bash
# Prerequisites
npm install -g pm2 serve pnpm

# Deploy
make pm2-start

# Manage
pm2 logs
pm2 status
```

#### 🔧 Manual Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
python install_llama.py

# Frontend
cd frontend
pnpm install
pnpm build

# Start services
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &
cd frontend && serve -s dist -l 3000 &
```

### Environment Configuration

#### Production Variables
```bash
# Backend
ENV=production
PYTHONPATH=/app

# Database (if external)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

#### External Database Setup
```sql
CREATE DATABASE textosql;
CREATE USER texttosql WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE texttosql TO texttosql;
```

### Monitoring & Logs

#### Docker
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps
```

#### PM2
```bash
# View logs
pm2 logs

# Monitor
pm2 monit
```

### Troubleshooting

**Common Issues:**
1. **Port conflicts**: Change ports in docker-compose.prod.yml
2. **Memory issues**: Increase Docker memory limits
3. **Model loading**: Ensure sufficient disk space (4GB+ for AI model)

**Health Checks:**
```bash
# Frontend
curl http://localhost:3000

# Backend API
curl http://localhost:3000/api/health
```

### Backup & Recovery

```bash
# Backup
docker exec postgres_container pg_dump -U postgres testdb > backup.sql

# Restore
docker exec -i postgres_container psql -U postgres testdb < backup.sql
```

## Architecture

- **Frontend**: React app with Nginx (port 3000)
- **Backend**: FastAPI on internal Docker network
- **Database**: PostgreSQL (internal network)
- **AI Model**: 4GB cached in persistent volume
- **Security**: Backend only accessible via proxy
