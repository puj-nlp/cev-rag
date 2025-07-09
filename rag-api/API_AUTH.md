# API Authentication

Esta API utiliza autenticación por API Key para proteger todos los endpoints.

## Configuración

### 1. Generar API Keys

Utiliza el script incluido para generar API keys seguras:

```bash
# Generar una API key
python generate_api_key.py

# Generar múltiples API keys
python generate_api_key.py --count 3

# Generar API keys con prefijo
python generate_api_key.py --prefix "prod_" --count 2
```

### 2. Configurar Variables de Entorno

Copia el archivo de ejemplo y configura tus API keys:

```bash
cp .env.example .env
```

Edita el archivo `.env` y establece tus API keys:

```bash
# Una sola API key
API_KEYS=tu_api_key_aqui

# Múltiples API keys (separadas por comas)
API_KEYS=key1,key2,key3
```

### 3. Deshabilitar Autenticación (Solo para Desarrollo)

Para deshabilitar la autenticación completamente, deja la variable `API_KEYS` vacía:

```bash
API_KEYS=
```

⚠️ **No recomendado para producción**

## Uso de la API

### Endpoints Protegidos

Todos los endpoints requieren autenticación excepto el health check (`GET /api/`):

- **Chat endpoints**: `/api/chats/*`
- **Admin endpoints**: `/api/admin/*`

### Formato de Autenticación

Incluye el API key en el header `Authorization` con formato Bearer:

```
Authorization: Bearer TU_API_KEY
```

### Ejemplos de Uso

#### cURL

```bash
# Health check (no requiere autenticación)
curl http://localhost:8000/api/

# Listar chats (requiere autenticación)
curl -H "Authorization: Bearer tu_api_key_aqui" \
     http://localhost:8000/api/chats

# Crear un nuevo chat
curl -X POST \
     -H "Authorization: Bearer tu_api_key_aqui" \
     -H "Content-Type: application/json" \
     -d '{"title": "Mi Chat", "session_id": "session123"}' \
     http://localhost:8000/api/chats

# Enviar mensaje
curl -X POST \
     -H "Authorization: Bearer tu_api_key_aqui" \
     -H "Content-Type: application/json" \
     -d '{"question": "¿Qué es la verdad?"}' \
     http://localhost:8000/api/chats/CHAT_ID/messages
```

#### JavaScript/Fetch

```javascript
const apiKey = 'tu_api_key_aqui';
const baseURL = 'http://localhost:8000/api';

// Configurar headers
const headers = {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
};

// Listar chats
const response = await fetch(`${baseURL}/chats`, {
    headers: headers
});

// Crear chat
const newChat = await fetch(`${baseURL}/chats`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
        title: 'Mi Chat',
        session_id: 'session123'
    })
});

// Enviar mensaje
const message = await fetch(`${baseURL}/chats/${chatId}/messages`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
        question: '¿Qué es la verdad?'
    })
});
```

#### Python Requests

```python
import requests

api_key = 'tu_api_key_aqui'
base_url = 'http://localhost:8000/api'
headers = {'Authorization': f'Bearer {api_key}'}

# Listar chats
response = requests.get(f'{base_url}/chats', headers=headers)

# Crear chat
new_chat = requests.post(
    f'{base_url}/chats',
    headers=headers,
    json={'title': 'Mi Chat', 'session_id': 'session123'}
)

# Enviar mensaje
message = requests.post(
    f'{base_url}/chats/{chat_id}/messages',
    headers=headers,
    json={'question': '¿Qué es la verdad?'}
)
```

## Respuestas de Error

### 401 Unauthorized

```json
{
    "detail": "API key required. Please provide Authorization header with Bearer token."
}
```

```json
{
    "detail": "Invalid API key"
}
```

## Mejores Prácticas de Seguridad

### 1. Gestión de API Keys

- **No hardcodees** las API keys en tu código
- **Usa variables de entorno** o gestores de secretos
- **Rota las keys regularmente**
- **Usa keys diferentes** para diferentes entornos (dev, staging, prod)

### 2. Almacenamiento Seguro

- Nunca commitees API keys al control de versiones
- Usa `.env` local para desarrollo
- Usa servicios como AWS Secrets Manager, Azure Key Vault, o HashiCorp Vault para producción

### 3. Monitoreo

- Registra intentos de autenticación fallidos
- Implementa rate limiting por API key
- Monitorea uso anómalo de las API keys

### 4. HTTPS

- **Siempre usa HTTPS** en producción
- Las API keys se transmiten en headers y pueden ser interceptadas en HTTP

## Solución de Problemas

### Error: "Import fastapi could not be resolved"

Esto es normal durante el desarrollo. Las dependencias se resolverán cuando ejecutes la aplicación con Docker.

### La autenticación no funciona

1. Verifica que `API_KEYS` esté configurado en `.env`
2. Asegúrate de que la API key no tenga espacios extra
3. Confirma que estás usando el formato correcto: `Bearer tu_api_key`

### Quiero deshabilitar temporalmente la autenticación

Establece `API_KEYS=` (vacío) en tu archivo `.env`.
