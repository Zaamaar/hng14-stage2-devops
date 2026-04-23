FROM node:18-alpine AS builder

WORKDIR /build
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine

# Create non-root user
RUN addgroup -g 1001 -S nodegroup && \
    adduser -S -u 1001 -G nodegroup nodeuser

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder --chown=nodeuser:nodegroup /build/node_modules ./node_modules

# Copy application code
COPY --chown=nodeuser:nodegroup . .

# Switch to non-root user
USER nodeuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/status/test',(r)=>{process.exit(0)}).on('error',()=>{process.exit(1)})"

EXPOSE 3000

CMD ["node", "app.js"]
