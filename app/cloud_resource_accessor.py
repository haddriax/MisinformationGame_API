from azure.core.exceptions import AzureError, HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient


class CloudResourcesAccessor:
    def __init__(self, az_key_vault_url: str):
        from logger import build_logger

        self.logger = build_logger(__name__, "INFO")

        # AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
        credential = DefaultAzureCredential()
        try:
            self.secret_client = SecretClient(
                vault_url=az_key_vault_url, credential=credential
            )
            # self.test_connection()
        except Exception as e:
            self.logger.error(f"Failed to initialize SecretClient: {e}")
            raise

    def test_connection(self):
        try:
            self.secret_client.list_properties_of_secrets()
            self.logger.info("Connection to Key Vault successful.")
        except HttpResponseError as e:
            self.logger.error(
                f"HTTP error occurred while testing Key Vault connection: {e}"
            )
            raise
        except AzureError as e:
            self.logger.error(
                f"Azure error occurred while testing Key Vault connection: {e}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred while testing Key Vault connection: {e}"
            )
            raise

    def get_secret(self, secret_name: str) -> str:
        try:
            self.logger.info(f"Fetching secret '{secret_name}' from Key Vault...")
            secret = self.secret_client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            self.logger.error(f"Error retrieving secret '{secret_name}': {e}")
            raise

    def get_blob_service_client(self, secret_name: str) -> BlobServiceClient:
        try:
            connection_string = self.get_secret(secret_name)
            return BlobServiceClient.from_connection_string(connection_string)
        except Exception as e:
            self.logger.error(f"Error creating BlobServiceClient: {e}")
            raise


# Usage example
if __name__ == "__main__":
    key_vault_url = "https://your-key-vault-name.vault.azure.net/"
    accessor = CloudResourcesAccessor(key_vault_url)
    blob_client = accessor.get_blob_service_client("BlobStorageConnectionString")
