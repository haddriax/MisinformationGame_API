import base64

from azure.core.exceptions import (AzureError, ResourceExistsError,
                                   ResourceNotFoundError)
from azure.storage.blob import BlobServiceClient, PublicAccess
from pydantic import BaseModel


class ImageBase64(BaseModel):
    """
    Represents an image in the form of a base64 encoded string.

    Attributes:
        path : str
            The path of the image file.
        image_data : str
            The base64 encoded string representing the image.
    """

    path: str
    image_data: str  # This should be a base64 encoded string


class BlobStorage:
    """
    Represents a class for interacting with Azure Blob Storage.

    Attributes:
        blob_service_client : str
            The path of the image file.
        logger : str
            The logger used for detailed logging.

    Methods:
        __init__(connection_string: str)
            Initializes a new instance of the BlobStorage class with a connection string.

        async upload_image_to_blob(
            container_name: str,
            item_name: str,
            image64: ImageBase64,
            overwrite_blob: bool = True,
            allow_anonymous_access: bool = True,
            verify_insert: bool = False,
        ) -> str
            Uploads an image to the blob storage container.
    """

    def __init__(self, connection_string: str):
        """
        Constructor for the class.

        Parameters:
            connection_string (str): The connection string used to create the BlobServiceClient.

        Raises:
            AzureError: If the BlobServiceClient fails to be created.

        """
        from logger import build_logger

        self.logger = build_logger(self.__class__.__name__, "INFO")

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        except AzureError as e:
            self.logger.error(f"Failed to create BlobServiceClient: {e}")
            raise

    async def upload_image_to_blob(
            self,
            container_name: str,
            item_name: str,
            image64: ImageBase64,
            overwrite_blob: bool = True,
            allow_anonymous_access: bool = True,
            verify_insert: bool = False,
    ) -> str:
        """
        Uploads an image to the blob storage container.

        Parameters:
            container_name (str): The name of the container in the blob storage.
            item_name (str): The name of the item (blob) to be created in the container.
            image64 (ImageBase64): The base64-encoded image data.
            overwrite_blob (bool): Indicates whether any already existing blob should be overwritten. Default is True.
            allow_anonymous_access (bool): Indicates whether the container allows anonymous access. Default is True.
            verify_insert (bool): Indicates whether to verify the insertion of the blob. Default is False.

        Returns:
            str: The URL of the newly uploaded item.

        Raises:
            AssertionError: If the input image is not an ImageBase64 instance.
            AzureError: If any Azure error occurs which could be due to creation, upload, verification, etc.
            ResourceExistsError: If the resource already exists and overwrite is set to false.
            ResourceNotFoundError: If the desired resource is not found.

        Example usage:
        ```
        image = ImageBase64(image_data="base64-encoded-image-data")
        blob_url = await upload_image_to_blob(
            container_name="my-container",
            item_name="my-image.jpg",
            image64=image,
            overwrite_blob=True,
            allow_anonymous_access=True,
            verify_insert=False
        )
        ```
"""

        assert isinstance(image64, ImageBase64), (
            "Trying to upload an image with a wrong format to a blob storage container."
        )

        try:
            # Connection to blob attempt.
            self.logger.info(
                f"Connecting to blob storage container '{container_name}'..."
            )
            container_client = self.blob_service_client.get_container_client(
                container_name
            )

            # Check if the container exists. If not, create it.
            # This could eventually be called only once when the BlobStorage object is created.
            if not container_client.exists():
                try:
                    # Quick note: a container is a folder for files hosted in the blob storage.
                    self.blob_service_client.create_container(
                        container_name,
                        public_access=PublicAccess.BLOB if allow_anonymous_access else None,
                    )
                    self.logger.info(f"Created container '{container_name}'.")
                except ResourceExistsError:
                    # In case the resource was created in then meantime.
                    self.logger.warning(f"Container '{container_name}' already exists.")

            blob_client = container_client.get_blob_client(item_name)
            image_bytes = base64.b64decode(image64.image_data)

            # Attempt to upload the data encoded in base64.
            # Setting overwrite to false will return a ResourceExistsError instead of overwriting it.
            try:
                blob_client.upload_blob(image_bytes, overwrite=overwrite_blob)
                self.logger.info(
                    f"Successfully uploaded blob '{item_name}' to container '{container_name}'."
                )

                # @todo Link that to the debug mode of the app.
                if verify_insert:
                    # Double check that the resource exists by using a query on the storage.
                    if blob_client.exists():
                        self.logger.info(
                            f"'{item_name}' exists in container '{container_name}'."
                        )
                    else:
                        self.logger.error(
                            f"'{item_name}' does not exist in container '{container_name}' after upload."
                        )
                        raise AzureError("Blob does not exist after upload")
                # --- End: verify_insert

                # In case of success, return the new uploaded item url.
                return blob_client.url

            # Only exceptions handling after that;
            except ResourceExistsError as e:
                self.logger.error(f"Failed to upload blob '{item_name}': {e}")
                raise
            except AzureError as e:
                self.logger.error(f"Failed to upload blob '{item_name}': {e}")
                raise
        except ResourceNotFoundError as e:
            self.logger.error(f"Resource not found: {e}")
            raise
        except AzureError as e:
            self.logger.error(f"Azure error occurred: {e}")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise

    async def delete_container(self, container_name: str):
        """
        Delete Container Method

        Parameters:
            container_name (str):
                The name of the container and its content to be deleted from the Blob Storage.

        Returns:
            None
        """

        try:
            container_client = self.blob_service_client.get_container_client(container_name)

            # Check if the container exists.
            if container_client.exists():
                # Delete the container
                self.blob_service_client.delete_container(container_name)
                self.logger.info(f"The container {container_name} has been deleted.")
            else:
                self.logger.warning("The container does not exist.")
        except Exception as e:
            self.logger.error(f"Could not delete the container: {e}")

    async def delete_image(self, container_name: str, image_name: str):
        """
         Deletes the specified image from the given container.
         If the image exists, it will be deleted and a success message will be logged.
         If the image does not exist, a warning message will be logged.
         If an exception occurs during the deletion process, an error message will be logged.

        Parameters:
            container_name (str):
                The name of the container where the image is stored.
            image_name (str):
                The name of the image to be deleted.

        Returns:
            None
        """

        try:
            # Get the blob client
            blob_client = self.blob_service_client.get_blob_client(container_name, image_name)

            # Check if the blob exists
            if blob_client.exists():
                # Delete the blob
                blob_client.delete_blob()
                self.logger.info(f"The blob {image_name} has been deleted from {container_name}.")
            else:
                self.logger.warning("The blob does not exist.")
        except Exception as e:
            self.logger.error("Could not delete the blob: ", e)
