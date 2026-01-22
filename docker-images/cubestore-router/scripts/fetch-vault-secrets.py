#!/usr/bin/env python3
"""
Fetch secrets from HashiCorp Vault for CubeJS configuration
This script retrieves BigQuery credentials and other secrets needed by CubeJS
"""

import os
import json
import sys
import requests
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VaultSecretsManager:
    def __init__(self):
        self.vault_url = os.getenv('VAULT_URL', 'https://vault.breeding-np.ag')
        self.vault_token = os.getenv('VAULT_TOKEN')
        self.environment = os.getenv('ENVIRONMENT', 'dev')
        self.namespace = os.getenv('VAULT_NAMESPACE', 'breeding')
        
        if not self.vault_token:
            logger.error("VAULT_TOKEN environment variable is required")
            sys.exit(1)

    def fetch_secret(self, secret_path):
        """Fetch a secret from Vault"""
        try:
            headers = {
                'X-Vault-Token': self.vault_token,
                'X-Vault-Namespace': self.namespace,
                'Content-Type': 'application/json'
            }
            
            url = f"{self.vault_url}/v1/{secret_path}"
            logger.info(f"Fetching secret from: {secret_path}")
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', {}).get('data', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch secret from {secret_path}: {e}")
            return {}

    def fetch_bigquery_credentials(self):
        """Fetch BigQuery service account credentials"""
        secret_path = f"kv/data/breeding/{self.environment}/bigquery"
        credentials = self.fetch_secret(secret_path)
        
        if not credentials:
            logger.warning("No BigQuery credentials found in vault")
            return None
            
        # Create service account key file
        service_account_key = {
            "type": "service_account",
            "project_id": credentials.get('project_id'),
            "private_key_id": credentials.get('private_key_id'),
            "private_key": credentials.get('private_key', '').replace('\\n', '\n'),
            "client_email": credentials.get('client_email'),
            "client_id": credentials.get('client_id'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{credentials.get('client_email', '')}"
        }
        
        # Write credentials to file
        credentials_path = '/cube/conf/bigquery-key.json'
        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
        
        with open(credentials_path, 'w') as f:
            json.dump(service_account_key, f, indent=2)
        
        logger.info(f"BigQuery credentials written to {credentials_path}")
        return credentials_path

    def fetch_cubestore_secrets(self):
        """Fetch Cubestore specific secrets"""
        secret_path = f"kv/data/breeding/{self.environment}/cubestore"
        secrets = self.fetch_secret(secret_path)
        
        if secrets:
            # Set environment variables for Cubestore
            cubestore_secrets = {
                'CUBESTORE_SERVER_NAME': secrets.get('server_name', 'cubestore-router:9999'),
                'CUBESTORE_META_PORT': secrets.get('meta_port', '9999'),
                'CUBESTORE_WORKER_PORT': secrets.get('worker_port', '10001'),
                'CUBESTORE_REMOTE_DIR': secrets.get('remote_dir', '/cube/data'),
                'CUBESTORE_META_ADDR': secrets.get('meta_addr', 'cubestore-router:9999'),
                'CUBESTORE_S3_REGION': secrets.get('s3_region'),
                'CUBESTORE_S3_BUCKET': secrets.get('s3_bucket'),
                'CUBESTORE_AWS_ACCESS_KEY_ID': secrets.get('aws_access_key_id'),
                'CUBESTORE_AWS_SECRET_ACCESS_KEY': secrets.get('aws_secret_access_key'),
            }
            
            # Set environment variables
            for key, value in cubestore_secrets.items():
                if value:
                    os.environ[key] = str(value)
                    logger.info(f"Set cubestore environment variable: {key}")
        
        return secrets

    def fetch_database_connection(self):
        """Fetch database connection details"""
        secret_path = f"kv/data/breeding/{self.environment}/database"
        db_secrets = self.fetch_secret(secret_path)
        
        if db_secrets:
            # Set database environment variables
            db_env_vars = {
                'CUBEJS_DB_TYPE': db_secrets.get('type', 'bigquery'),
                'CUBEJS_DB_HOST': db_secrets.get('host'),
                'CUBEJS_DB_PORT': db_secrets.get('port', '5432'),
                'CUBEJS_DB_NAME': db_secrets.get('database'),
                'CUBEJS_DB_USER': db_secrets.get('username'),
                'CUBEJS_DB_PASS': db_secrets.get('password'),
                'CUBEJS_DB_SSL': db_secrets.get('ssl', 'true'),
            }
            
            for key, value in db_env_vars.items():
                if value:
                    os.environ[key] = str(value)
                    logger.info(f"Set database environment variable: {key}")
        
        return db_secrets

def main():
    """Main function to fetch all required secrets for Cubestore Router"""
    logger.info("🔐 Starting vault secrets fetch for Cubestore Router...")
    
    vault_manager = VaultSecretsManager()
    
    # Fetch BigQuery credentials (may be needed for some operations)
    bigquery_creds_path = vault_manager.fetch_bigquery_credentials()
    if bigquery_creds_path:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = bigquery_creds_path
        logger.info("✅ BigQuery credentials configured")
    
    # Fetch Cubestore secrets
    cubestore_secrets = vault_manager.fetch_cubestore_secrets()
    if cubestore_secrets:
        logger.info("✅ Cubestore secrets configured")
    
    # Fetch database connection details (for metadata)
    db_secrets = vault_manager.fetch_database_connection()
    if db_secrets:
        logger.info("✅ Database connection configured")
    
    # Set Cubestore Router specific configuration
    os.environ['CUBESTORE_SERVER_NAME'] = os.environ.get('CUBESTORE_SERVER_NAME', 'cubestore-router:9999')
    os.environ['CUBESTORE_META_PORT'] = os.environ.get('CUBESTORE_META_PORT', '9999')
    
    logger.info("🚀 All secrets fetched successfully for Cubestore Router!")

if __name__ == '__main__':
    main()