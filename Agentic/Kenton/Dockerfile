# Multi-stage Dockerfile for Kenton Deep Research Agent

# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ .

# Build the Next.js app
RUN npm run build

# Stage 2: Python Backend + Serve Frontend
FROM python:3.12-slim

# Install Node.js for serving the Next.js app
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/node_modules ./frontend/node_modules
COPY --from=frontend-builder /app/frontend/package.json ./frontend/package.json

# Create a startup script
RUN echo '#!/bin/bash\n\
cd /app/frontend && npm start &\n\
cd /app && python streamlined_api_server.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 3000 8001

# Environment variables
ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1

# Start both services
CMD ["/app/start.sh"]