# Window to Truth: Chatbot for the Colombian Truth Commission

This project is a query application about the Colombian conflict using the RAG (Retrieval-Augmented Generation) technique. The application allows users to ask questions about the armed conflict in Colombia and receive answers generated with the help of relevant documents retrieved from the Truth Commission's Clarification Archive.

## Project Structure

- `rag-api/`: Backend with FastAPI
- `rag-ui/`: Frontend with React
- `MilvusVolumes/`: Persistent storage for the Milvus database

## Requirements

- Docker and Docker Compose
- OpenAI API key

## Configuration

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and provide your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

3. If you have custom data to load into Milvus, make sure it's available in the `rag-api/data/` directory.

## Starting the Application

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Loading Data into Milvus

If you need to load data into the Milvus database, you can run the following command after the containers are running:

```bash
docker-compose exec rag-api python -m scripts.build_milvus_db
```

## Services

- **rag-api**: FastAPI backend that manages RAG logic and communication with OpenAI and Milvus
- **rag-ui**: React frontend that provides the user interface
- **milvus**: Vector database for storing and searching embeddings

## Development

### Backend (FastAPI)

To develop the backend locally:

```bash
cd rag-api
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (React)

To develop the frontend locally:

```bash
cd rag-ui
npm install
npm start
```
