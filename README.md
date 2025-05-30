# research_automation

An AI-powered research assistant to help you manage, explore, and interact with academic papers and topics. Upload documents, extract structured insights, and ask questions—all within a topic-centric workspace.

Status: In development — Document pipeline is functional. Chat and user/topic services are in progress.

## Features
### MVP Goals (In Progress)
- Upload and store multiple documents per topic
- Document ingestion pipeline (end-to-end)
- User and topic management
- Chat with documents (toggle sources, citation support)
- Key info extraction (methods, results, summary, etc.)
- Citation extraction
- Session history (multi-turn memory)
- Basic UI

### Planned Enhancements
- Research discovery (recommendations, trends)
- Topic-based collaboration (shared workspaces)
- Fine-grained access control
- Integration with external tools (Zotero, Arxiv, etc.)

### Architecture Overview
- FastAPI – Backend API server
- Celery + Redis – Document ingestion and background tasks
- MongoDB – Storage (documents, metadata, embeddings, insights)
- Ollama – Local LLM and embedding models
- Vector Search – Similarity search with source citation
- (Planned): Authentication, observability, hybrid search

### Modular Services
- Storage Service
- User & Topic Service
- Search Service
- Chat Service
- Observability & Metrics

 Current Capabilities
- [-] Document ingestion with metadata & embeddings
- [-] PDF batch processing with Celery
- [-] Storage by topic with structured metadata
- [-] Ready to chat with LLMs (service incomplete)



## Setup Instructions

#### Start containers (docker compose also provided, to be used in prod)
```bash
docker run -d -p 6379:6379 redis:latest

docker run -d -p 27017:27017 -v mongodb_data:/data/db mongo:latest

docker run -d   -v ollama:/root/.ollama   -p 11434:11434   --name ollama   ollama/ollama

docker exec -it ollama ollama pull nomic-embed-text

docker exec -it ollama ollama pull llama3.2:3b
```

### Start backend services

#### Start celery
`celery -A app.celery_worker worker -Q ingestion -l INFO`

#### Start Fastapi
`uvicorn app.main:app --host 0.0.0.0 --port 8000`



### Roadmap & Todos
- Push user/topic services
- Finalize chat interface (currently non-functional)
- Evaluate replacing Celery+Redis with FastAPI background tasks
- Add observability (logs, metrics)
- JWT auth → OAuth later

#### Contributing
- Contributions, bug reports, and feedback are welcome!
- Fork the repo
- Create a new branch (feat/feature-name)
- Make your changes
- Submit a pull request
