````markdown
# Company OS

Company OS is a modular company knowledge and operations platform built with a FastAPI backend, Next.js frontend, PostgreSQL, pgvector, MinIO, and background ingestion workers.

## Tech Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python
- **Database:** PostgreSQL
- **Vector Search:** pgvector
- **Object Storage:** MinIO
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Embeddings:** Sentence Transformers
- **Authentication:** JWT + bcrypt
- **Background Processing:** Python ingestion worker
- **Containers:** Docker / Docker Compose

---

## Prerequisites

Install the following:

- Git
- Docker Desktop
- Python 3.11+
- Node.js 20+
- npm

Make sure Docker Desktop is running.

---

## Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd company-os
```
````

---

# Backend Setup

Go to the backend:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## Environment Variables

Create:

```text
backend/.env
```

Add the required configuration:

```env
DATABASE_URL=postgresql://companyos:companyos@localhost:5432/companyos

MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=companyos

JWT_SECRET_KEY=change-this-secret
```

Use the project's existing `.env.example` if available.

---

# Start Infrastructure

From the project root:

```powershell
docker compose up -d
```

Check running containers:

```powershell
docker ps
```

You should have the PostgreSQL and MinIO services running.

---

# Database Setup

From the `backend` directory with the virtual environment activated:

```powershell
alembic upgrade head
```

Check the current migration:

```powershell
alembic current
```

Check migration history:

```powershell
alembic history
```

---

# Start Backend

From:

```text
company-os/backend
```

Run:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

# Start MinIO

MinIO runs through Docker Compose.

The MinIO console is normally available at:

```text
http://localhost:9001
```

Use the credentials configured in your Docker Compose / environment configuration.

Documents uploaded to Company OS are stored in MinIO.

---

# Ingestion Worker

The ingestion worker processes uploaded documents and performs the document ingestion pipeline.

Worker location:

```text
backend/workers/ingestion_worker.py
```

From the `backend` directory:

```powershell
python workers/ingestion_worker.py
```

The worker is responsible for processing documents through the ingestion pipeline, including extracting document text, creating chunks, generating embeddings, and storing the required data for retrieval.

Keep the worker running in a separate terminal while using document ingestion.

---

# Frontend Setup

Open another terminal.

Go to:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Create:

```text
frontend/.env.local
```

Add:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# Running the Complete Application

Use separate terminals.

### Terminal 1 — Infrastructure

From the project root:

```powershell
docker compose up -d
```

### Terminal 2 — Backend

```powershell
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

### Terminal 3 — Ingestion Worker

```powershell
cd backend
.venv\Scripts\activate
python workers/ingestion_worker.py
```

### Terminal 4 — Frontend

```powershell
cd frontend
npm run dev
```

Then open:

```text
http://localhost:3000
```

---

# Authentication

Register a new user through the application or API.

API endpoint:

```text
POST /auth/register
```

Login:

```text
POST /auth/login
```

Current authenticated user:

```text
GET /auth/me
```

Swagger can be used to test these endpoints:

```text
http://localhost:8000/docs
```

---

# Useful Docker Commands

Start services:

```powershell
docker compose up -d
```

Stop services:

```powershell
docker compose down
```

View containers:

```powershell
docker ps
```

View logs:

```powershell
docker compose logs
```

View PostgreSQL logs:

```powershell
docker compose logs postgres
```

View MinIO logs:

```powershell
docker compose logs minio
```

Restart services:

```powershell
docker compose restart
```

---

# Useful Database Commands

Open PostgreSQL:

```powershell
docker exec -it companyos-postgres psql -U companyos -d companyos
```

List tables:

```sql
\dt
```

Check users:

```sql
SELECT * FROM users;
```

Check documents:

```sql
SELECT * FROM documents;
```

Check document chunks:

```sql
SELECT * FROM document_chunks;
```

Exit PostgreSQL:

```sql
\q
```

---

# Useful Development Commands

Create a new migration:

```powershell
alembic revision --autogenerate -m "description"
```

Apply migrations:

```powershell
alembic upgrade head
```

Rollback one migration:

```powershell
alembic downgrade -1
```

Run frontend:

```powershell
npm run dev
```

Build frontend:

```powershell
npm run build
```

---

# Project Structure

```text
company-os/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── database/
│   │
│   ├── migrations/
│   ├── workers/
│   │   └── ingestion_worker.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── .env.local
│
├── docker-compose.yml
└── README.md
```

---

## Stop the Application

Stop the frontend and backend with:

```text
Ctrl + C
```

Stop Docker services:

```powershell
docker compose down
```
