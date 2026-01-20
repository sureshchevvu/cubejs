# Cubestore Router Dockerfile
FROM cubejs/cubestore:latest

# Set working directory
WORKDIR /cube

# Environment variables specific to Cubestore Router
ENV CUBESTORE_SERVER_NAME=cubestore-router:9999
ENV CUBESTORE_META_PORT=9999
ENV CUBESTORE_REMOTE_DIR=/cube/data

# Create data directory
RUN mkdir -p /cube/data

# Expose the meta port
EXPOSE 9999

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD cubestore --version || exit 1

# Start Cubestore Router
CMD ["cubestore"]