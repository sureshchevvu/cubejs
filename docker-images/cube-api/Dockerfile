# Cube API Dockerfile
FROM cubejs/cube:latest

# Set working directory
WORKDIR /cube/conf

# Environment variables specific to Cube API
ENV CUBEJS_API_SECRET="your-secret-key"
ENV CUBEJS_WEB_SOCKETS=true

# Expose the API port
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:4000/cubejs-api/v1/load || exit 1

# Start Cube API server
CMD ["node", "index.js"]