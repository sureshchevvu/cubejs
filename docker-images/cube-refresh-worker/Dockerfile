# Cube Refresh Worker Dockerfile
FROM cubejs/cube:latest

# Set working directory
WORKDIR /cube/conf

# Environment variables specific to Refresh Worker
ENV CUBEJS_REFRESH_WORKER=true
ENV CUBEJS_SCHEDULED_REFRESH_DEFAULT=true

# Expose worker port (if needed for monitoring)
EXPOSE 80

# Health check for refresh worker
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD ps aux | grep -q '[n]ode' || exit 1

# Start Cube Refresh Worker
CMD ["node", "index.js"]