# Cube API Dockerfile
FROM cubejs/cube:latest

# Accept build arguments for vault configuration
ARG ENVIRONMENT
ARG VAULT_URL
ARG VAULT_TOKEN
ARG VAULT_NAMESPACE

# Install Python and required packages for secrets management
USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for vault secrets
RUN pip3 install requests hvac boto3 google-cloud-bigquery

# Set working directory
WORKDIR /cube/conf

# Copy secrets fetching script from breeding-cube project
COPY scripts/ /cube/scripts/
RUN chmod +x /cube/scripts/fetch-vault-secrets.py

# Create startup script that fetches secrets before starting Cube
RUN cat > /cube/start.sh << 'EOF' \
#!/bin/bash \
set -e \
\
echo "🔐 Fetching secrets from vault..." \
/usr/bin/python3 /cube/scripts/fetch-vault-secrets.py \
\
echo "🚀 Starting Cube API server..." \
exec node index.js \
EOF

RUN chmod +x /cube/start.sh

# Switch back to cube user
USER cube

# Set environment variables from build args
ENV ENVIRONMENT=${ENVIRONMENT}
ENV VAULT_URL=${VAULT_URL}
ENV VAULT_TOKEN=${VAULT_TOKEN}
ENV VAULT_NAMESPACE=${VAULT_NAMESPACE}

# Environment variables - will be populated by secrets script
ENV CUBEJS_WEB_SOCKETS=true
ENV CUBEJS_REFRESH_WORKER=false

# Expose the API port
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:4000/cubejs-api/v1/load || exit 1

# Start with secrets fetching script
CMD ["/cube/start.sh"]