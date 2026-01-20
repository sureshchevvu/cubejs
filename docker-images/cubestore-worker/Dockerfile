# Cubestore Worker Dockerfile
FROM cubejs/cubestore:latest

# Set working directory
WORKDIR /cube

# Environment variables specific to Cubestore Worker
ENV CUBESTORE_WORKER_PORT=10001
ENV CUBESTORE_REMOTE_DIR=/cube/data
ENV CUBESTORE_META_ADDR=cubestore-router:9999

# Create data directory
RUN mkdir -p /cube/data

# Expose the worker port
EXPOSE 10001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD cubestore --version || exit 1

# Start Cubestore Worker
CMD ["cubestore"]