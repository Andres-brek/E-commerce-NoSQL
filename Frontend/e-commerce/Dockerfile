# ── Etapa 1: construir la app ──────────────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app

# Primero solo los manifiestos para aprovechar la caché de Docker:
# si package.json no cambia, npm install no se vuelve a correr.
COPY package*.json .
RUN npm install

# Luego el código fuente
COPY . .
RUN npm run build
# Resultado: /app/build/ con HTML, CSS y JS listos para producción


# ── Etapa 2: servir con Nginx ──────────────────────────────────────────────
FROM nginx:alpine

# Copia solo la carpeta build de la etapa anterior (Node no viene aquí)
COPY --from=build /app/build /usr/share/nginx/html

# Reemplaza la config por defecto de Nginx con la nuestra
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
