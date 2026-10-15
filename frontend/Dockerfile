# Stage 1: build the React app with Node
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: serve static files with an unprivileged Nginx (runs as non-root uid 101)
FROM nginxinc/nginx-unprivileged:1.30-alpine
USER root
RUN apk upgrade --no-cache
USER 101
ENV BACKEND_URL=http://backend:8000
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/templates/default.conf.template
EXPOSE 8080
