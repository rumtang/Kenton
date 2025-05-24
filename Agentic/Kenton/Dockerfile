# Multi-stage Dockerfile for Kenton Deep Research Agent with Memory Support

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

# Install system dependencies including Redis client libraries (optional)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code including new memory management
COPY . .

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/node_modules ./frontend/node_modules
COPY --from=frontend-builder /app/frontend/package.json ./frontend/package.json

# Create a startup script that uses the new API server
RUN echo '#!/bin/bash\n\
echo "Starting Kenton Deep Research Agent..."\n\
echo "Memory system: ${USE_REDIS:-false}"\n\
cd /app/frontend && npm start &\n\
cd /app && python fixed_api_server.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 3000 8001

# Environment variables
ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8001

# Optional Redis configuration (set these in Cloud Run or docker-compose)
# ENV REDIS_URL=redis://localhost:6379
# ENV USE_REDIS=false

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Start both services
CMD ["/app/start.sh"]