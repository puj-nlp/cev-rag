FROM node:18-alpine as build

WORKDIR /app

# Copiar los archivos package*.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Construir la aplicación
RUN npm run build

# Etapa de producción
FROM nginx:alpine

# Copiar la configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar los archivos de build del frontend
COPY --from=build /app/build /usr/share/nginx/html

# Generar config.js en runtime (MAINTENANCE_MODE, MAINTENANCE_MESSAGE)
COPY docker-entrypoint.d/40-app-config.sh /docker-entrypoint.d/40-app-config.sh
RUN chmod +x /docker-entrypoint.d/40-app-config.sh

# Exponer el puerto 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
