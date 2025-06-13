# Ventana a la Verdad: Chatbot para la Comisión de la Verdad de Colombia

Este proyecto es una aplicación de consulta sobre el conflicto colombiano utilizando la técnica RAG (Retrieval-Augmented Generation). La aplicación permite a los usuarios hacer preguntas sobre el conflicto armado en Colombia y recibir respuestas generadas con la ayuda de documentos relevantes recuperados de la base de datos de la Comisión de la Verdad.

## Estructura del proyecto

- `rag-api/`: Backend con FastAPI
- `rag-ui/`: Frontend con React
- `MilvusVolumes/`: Almacenamiento persistente para la base de datos Milvus

## Requisitos

- Docker y Docker Compose
- Clave API de OpenAI

## Configuración

1. Copia el archivo `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edita el archivo `.env` y proporciona tu clave de API de OpenAI:
   ```
   OPENAI_API_KEY=tu_clave_api_de_openai
   ```

3. Si tienes datos personalizados para cargar en Milvus, asegúrate de que estén disponibles en el directorio `rag-api/data/`.

## Iniciar la aplicación

```bash
docker-compose up --build
```

La aplicación estará disponible en:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

## Carga de datos en Milvus

Si necesitas cargar datos en la base de datos Milvus, puedes ejecutar el siguiente comando después de que los contenedores estén funcionando:

```bash
docker-compose exec rag-api python -m scripts.build_milvus_db
```

## Servicios

- **rag-api**: Backend con FastAPI que gestiona la lógica RAG y la comunicación con OpenAI y Milvus
- **rag-ui**: Frontend con React que proporciona la interfaz de usuario
- **milvus**: Base de datos vectorial para almacenar y buscar embeddings

## Desarrollo

### Backend (FastAPI)

Para desarrollar localmente el backend:

```bash
cd rag-api
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (React)

Para desarrollar localmente el frontend:

```bash
cd rag-ui
npm install
npm start
```
