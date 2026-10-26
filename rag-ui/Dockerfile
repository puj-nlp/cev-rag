FROM node:18-alpine as build

WORKDIR /app

# Copiar los archivos package*.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Construir la aplicación
# - Sin runtime chunk inline: permite una CSP con script-src 'self'
# - Sin source maps en producción
ARG REACT_APP_SITE_URL=https://localhost
ENV INLINE_RUNTIME_CHUNK=false \
    GENERATE_SOURCEMAP=false \
    REACT_APP_SITE_URL=${REACT_APP_SITE_URL}
RUN npm run build

# Etapa de producción
FROM nginx:1.27-alpine

# Plantilla de nginx (envsubst solo sobre variables SITE_*) y fragmentos compartidos
ENV NGINX_ENVSUBST_FILTER=^SITE_ \
    SITE_DOMAIN=localhost
COPY nginx/templates/ /etc/nginx/templates/
COPY nginx/snippets/ /etc/nginx/snippets/
RUN rm -f /etc/nginx/conf.d/default.conf

# Copiar los archivos de build del frontend
COPY --from=build /app/build /usr/share/nginx/html

# Certificado Origin CA de Cloudflare montado en /etc/nginx/certs (origin.pem / origin.key)
EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
