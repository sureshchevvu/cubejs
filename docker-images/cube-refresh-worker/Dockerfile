# Cube Refresh Worker Dockerfile
FROM cubejs/cube:latest

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
WORKDIR /cube/conf

# Copy secrets fetching script
COPY scripts/ /cube/scripts/
RUN chmod +x /cube/scripts/fetch-vault-secrets.py

# Create startup script that fetches secrets before starting worker
RUN cat > /cube/start.sh << 'EOF' \
&& echo '#!/bin/bash' >> /cube/start.sh \
&& echo 'set -e' >> /cube/start.sh \
&& echo '' >> /cube/start.sh \
&& echo 'echo "🔐 Fetching secrets from vault..."' >> /cube/start.sh \
&& echo 'python3 /cube/scripts/fetch-vault-secrets.py' >> /cube/start.sh \
&& echo '' >> /cube/start.sh \
&& echo 'echo "🔄 Starting Cube Refresh Worker..."' >> /cube/start.sh \
&& echo 'exec node index.js' >> /cube/start.sh

RUN chmod +x /cube/start.sh

# Switch back to cube user
USER cube

# Set environment variables from build args
ENV ENVIRONMENT=${ENVIRONMENT}
ENV VAULT_URL=${VAULT_URL}
ENV VAULT_TOKEN=${VAULT_TOKEN}
ENV VAULT_NAMESPACE=${VAULT_NAMESPACE}
ENV AWS_REGION=${AWS_REGION}
ENV AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}
ENV AWS_DEFAULT_REGION=${AWS_REGION}

# Environment variables specific to Refresh Worker
ENV CUBEJS_REFRESH_WORKER=true
ENV CUBEJS_SCHEDULED_REFRESH_DEFAULT=true

# Expose worker port (if needed for monitoring)
EXPOSE 80

# Health check for refresh worker
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD ps aux | grep -q '[n]ode' || exit 1

# Start with secrets fetching script
CMD ["/cube/start.sh"]