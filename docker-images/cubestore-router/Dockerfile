# Cubestore Router Dockerfile
FROM cubejs/cubestore:latest

# Accept build arguments for vault configuration
ARG ENVIRONMENT
ARG VAULT_URL
ARG VAULT_TOKEN
ARG VAULT_NAMESPACE
ARG AWS_REGION
ARG AWS_ACCOUNT_ID

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
WORKDIR /cube

# Copy secrets fetching script
COPY scripts/ /cube/scripts/
RUN chmod +x /cube/scripts/fetch-vault-secrets.py

# Create startup script that fetches secrets before starting router
RUN cat > /cube/start.sh << 'EOF'\
#!/bin/bash\
set -e\
\
echo "🔐 Fetching secrets from vault..."\
python3 /cube/scripts/fetch-vault-secrets.py\
\
echo "🌐 Starting Cubestore Router..."\
exec cubestore\
EOF

RUN chmod +x /cube/start.sh

# Create data directory
RUN mkdir -p /cube/data

# Switch back to cubestore user
USER cubestore

# Set environment variables from build args
ENV ENVIRONMENT=${ENVIRONMENT}
ENV VAULT_URL=${VAULT_URL}
ENV VAULT_TOKEN=${VAULT_TOKEN}
ENV VAULT_NAMESPACE=${VAULT_NAMESPACE}
ENV AWS_REGION=${AWS_REGION}
ENV AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}
ENV AWS_DEFAULT_REGION=${AWS_REGION}

# Environment variables specific to Cubestore Router
ENV CUBESTORE_SERVER_NAME=cubestore-router:9999
ENV CUBESTORE_META_PORT=9999
ENV CUBESTORE_REMOTE_DIR=/cube/data

# Expose the meta port
EXPOSE 9999

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD cubestore --version || exit 1

# Start with secrets fetching script
CMD ["/cube/start.sh"]