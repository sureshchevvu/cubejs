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

    def fetch_cube_secrets(self):
        """Fetch CubeJS specific secrets"""
        secret_path = f"kv/data/breeding/{self.environment}/cubejs"
        secrets = self.fetch_secret(secret_path)
        
        if secrets:
            # Set environment variables for CubeJS
            cube_secrets = {
                'CUBEJS_API_SECRET': secrets.get('api_secret'),
                'CUBEJS_DB_HOST': secrets.get('db_host'),
                'CUBEJS_DB_NAME': secrets.get('db_name'), 
                'CUBEJS_DB_USER': secrets.get('db_user'),
                'CUBEJS_DB_PASS': secrets.get('db_password'),
                'CUBEJS_JWT_SECRET': secrets.get('jwt_secret'),
            }
            
            # Set environment variables
            for key, value in cube_secrets.items():
                if value:
                    os.environ[key] = str(value)
                    logger.info(f"Set environment variable: {key}")
        
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
    """Main function to fetch all required secrets"""
    logger.info("🔐 Starting vault secrets fetch for CubeJS...")
    
    vault_manager = VaultSecretsManager()
    
    # Fetch BigQuery credentials
    bigquery_creds_path = vault_manager.fetch_bigquery_credentials()
    if bigquery_creds_path:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = bigquery_creds_path
        os.environ['CUBEJS_DB_BQ_KEY_FILE'] = bigquery_creds_path
        logger.info("✅ BigQuery credentials configured")
    
    # Fetch CubeJS secrets
    cube_secrets = vault_manager.fetch_cube_secrets()
    if cube_secrets:
        logger.info("✅ CubeJS secrets configured")
    
    # Fetch database connection details
    db_secrets = vault_manager.fetch_database_connection()
    if db_secrets:
        logger.info("✅ Database connection configured")
    
    # Set additional CubeJS configuration
    os.environ['CUBEJS_WEB_SOCKETS'] = 'true'
    os.environ['CUBEJS_DEV_MODE'] = 'false' if vault_manager.environment == 'prod' else 'true'
    os.environ['CUBEJS_CACHE_AND_QUEUE_DRIVER'] = 'redis'
    
    logger.info("🚀 All secrets fetched successfully!")

if __name__ == '__main__':
    main()