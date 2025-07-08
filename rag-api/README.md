# RAG API

Backend API para el sistema de consultas sobre el conflicto colombiano usando RAG (Retrieval-Augmented Generation).

## 🔐 Autenticación

Esta API utiliza autenticación por API Key. **Todos los endpoints requieren autenticación excepto el health check.**

### Configuración Rápida

1. **Generar API Key:**
   ```bash
   python generate_api_key.py
   ```

2. **Configurar .env:**
   ```bash
   cp .env.example .env
   # Editar .env y establecer API_KEYS=tu_api_key_generada
   ```

3. **Usar la API:**
   ```bash
   curl -H "Authorization: Bearer tu_api_key" http://localhost:8000/api/chats
   ```

📖 **Ver [API_AUTH.md](API_AUTH.md) para documentación completa de autenticación**

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

```bash
# Desde el directorio raíz del proyecto
docker-compose up --build
```

### Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar
python main.py
```

## 📊 Endpoints Principales

### Health Check (No requiere autenticación)
```bash
GET /api/
```

### Chat Management (Requiere API Key)
```bash
# Listar chats
GET /api/chats
Authorization: Bearer tu_api_key

# Crear chat
POST /api/chats
Authorization: Bearer tu_api_key
Content-Type: application/json
{
    "title": "Mi Chat",
    "session_id": "session123"
}

# Enviar mensaje
POST /api/chats/{chat_id}/messages
Authorization: Bearer tu_api_key
Content-Type: application/json
{
    "question": "¿Qué es la verdad?"
}
```

### Admin Endpoints (Requiere API Key)
```bash
# Estadísticas
GET /api/admin/stats
Authorization: Bearer tu_api_key

# Buscar mensajes
GET /api/admin/search?query=verdad
Authorization: Bearer tu_api_key
```

## 🧪 Pruebas

### Probar Autenticación
```bash
# Probar sin API key (debería fallar)
python test_auth.py

# Probar con API key
python test_auth.py --api-key tu_api_key_aqui

# O usar variable de entorno
export API_KEY=tu_api_key_aqui
python test_auth.py
```

### Ejemplos de Uso

#### Python
```python
import requests

headers = {'Authorization': 'Bearer tu_api_key'}
response = requests.get('http://localhost:8000/api/chats', headers=headers)
```

#### JavaScript
```javascript
const headers = {'Authorization': 'Bearer tu_api_key'};
const response = await fetch('http://localhost:8000/api/chats', {headers});
```

#### cURL
```bash
curl -H "Authorization: Bearer tu_api_key" http://localhost:8000/api/chats
```

## 🔧 Configuración

### Variables de Entorno (.env)

```bash
# Autenticación
API_KEYS=tu_api_key_aqui

# Base de datos
STORAGE_TYPE=sqlite
SQLITE_PATH=data/chat_sessions.db

# OpenAI
OPENAI_API_KEY=tu_openai_key

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

### Deshabilitar Autenticación (Solo Desarrollo)

```bash
# En .env
API_KEYS=
```

⚠️ **No recomendado para producción**

## 📚 Documentación API

Una vez que la aplicación esté ejecutándose:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Herramientas

- `generate_api_key.py`: Generar API keys seguras
- `test_auth.py`: Probar autenticación
- `cli_db_manager.py`: Gestión de base de datos

## 🔒 Seguridad

- Las API keys se validan en cada request a endpoints protegidos
- Usa HTTPS en producción
- Rota las API keys regularmente
- No commitees API keys al repositorio

## 📁 Estructura del Proyecto

```
rag-api/
├── src/                          # Código fuente
│   ├── adapters/                 # Adaptadores (controladores, repos)
│   ├── application/              # Casos de uso
│   ├── domain/                   # Entidades de dominio
│   └── infrastructure/           # Infraestructura (config, auth)
├── data/                         # Datos y base de datos
├── scripts/                      # Scripts de utilidad
├── generate_api_key.py           # Generador de API keys
├── test_auth.py                  # Pruebas de autenticación
├── API_AUTH.md                   # Documentación de autenticación
└── requirements.txt              # Dependencias
```

## 🐛 Solución de Problemas

### "Import fastapi could not be resolved"
Esto es normal durante desarrollo. Las dependencias se resuelven en Docker.

### "API key required"
Asegúrate de:
1. Tener `API_KEYS` configurado en `.env`
2. Usar el formato correcto: `Authorization: Bearer tu_api_key`
3. No tener espacios extra en la API key

### Error de conexión a Milvus
Verifica que Milvus esté ejecutándose:
```bash
docker-compose ps
```

## 📞 Soporte

Para problemas específicos de autenticación, consulta [API_AUTH.md](API_AUTH.md).
