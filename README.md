# Doc Chat — Multi-Document Question Answering System

Doc Chat is an enterprise-style Retrieval-Augmented Generation (RAG) application that lets users upload multiple documents and ask natural-language questions across them, with answers grounded in cited source passages.

The project was built end-to-end — backend, frontend, and infrastructure — to mirror the architecture, patterns, and production concerns you'd find in a real enterprise AI product.

## Features

- **Multi-document upload** — supports PDF, DOCX, and TXT files
- **Full RAG pipeline** — document extraction → cleaning → chunking → embedding → vector storage → retrieval → LLM-generated answer
- **Source-cited answers** — responses reference the specific document passages used to generate them
- **Chat interface** — persistent conversation history per user, with multi-turn Q&A
- **User authentication** — JWT-based auth and per-user document isolation

## Tech Stack

**Backend**
- Python, FastAPI
- LangChain
- OpenAI API (GPT-4) for generation, `text-embedding-3-large` for embeddings
- ChromaDB (vector store)
- PostgreSQL + SQLAlchemy
- JWT authentication

**Frontend**
- React, TypeScript
- Tailwind CSS

**Infrastructure**
- Docker / Docker Compose
- GitHub Actions (CI/CD)
- AWS Lambda + S3 (deployment target)

## Architecture

```
Client (React/TS) 
      │
      ▼
FastAPI Backend
 ├── api/            → route handlers
 ├── models/         → SQLAlchemy models
 ├── schemas/        → Pydantic request/response schemas
 ├── services/       → business logic
 ├── database/        → DB session & config
 ├── authentication/ → JWT auth & user management
 ├── rag/            → document processing & RAG pipeline
 └── utils/          → shared helpers
      │
      ▼
PostgreSQL (metadata, users, chat history)
ChromaDB (vector embeddings)
```

### Data model

- **Users** — account and auth data
- **Documents** — uploaded file records per user
- **Document_Metadata** — extracted metadata, processing status
- **Chat_History** — conversation sessions
- **Messages** — individual Q&A turns with source citations

## Getting Started

### Prerequisites

- Docker & Docker Compose
- An OpenAI API key

### Setup

1. Clone the repository
   ```bash
   git clone https://github.com/bhautik7/doc-chat.git
   cd doc-chat
   ```

2. Create a `.env` file in the `backend` directory with the required environment variables (database URL, OpenAI API key, JWT secret, etc.)

3. Start the application
   ```bash
   docker-compose up --build
   ```

4. The backend API will be available with interactive Swagger docs at `http://localhost:8000/docs`, and the frontend at `http://localhost:3000` (adjust ports as configured in `docker-compose.yml`).

### Running locally without Docker

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
doc-chat/
├── backend/           # FastAPI application, RAG pipeline, database
├── frontend/           # React + TypeScript client
├── docker-compose.yml  # Multi-service orchestration
└── .vscode/            # Editor configuration
```

## Roadmap

- [ ] Unit and integration test coverage
- [ ] CI/CD pipeline via GitHub Actions
- [ ] AWS deployment (Lambda + S3)
- [ ] Support for additional file types
- [ ] Multi-user document sharing/permissions

## License

MIT
