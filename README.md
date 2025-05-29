# research_automation


### To run

Start containers (docker compose also provided, to be used in prod)
```bash
docker run -d -p 6379:6379 redis:latest

docker run -d -p 27017:27017 -v mongodb_data:/data/db mongo:latest

docker run -d   -v ollama:/root/.ollama   -p 11434:11434   --name ollama   ollama/ollama

docker exec -it ollama ollama pull nomic-embed-text

docker exec -it ollama ollama pull llama3.2:3b
```


Start celery
`celery -A app.celery_worker worker -Q ingestion -l INFO`

Start Fastapi
`uvicorn app.main:app --host 0.0.0.0 --port 8000`