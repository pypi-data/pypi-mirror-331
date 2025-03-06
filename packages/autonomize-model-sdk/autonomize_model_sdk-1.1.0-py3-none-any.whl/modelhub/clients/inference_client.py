"""Client for interacting with inference endpoints."""

import mimetypes
import os
from typing import Any, BinaryIO, Dict, Optional, Tuple, Union
from urllib.parse import urlparse

import requests

from ..core import BaseClient, ModelHubException
from ..core.response import handle_response
from ..utils import setup_logger

logger = setup_logger(__name__)


class InferenceClient(BaseClient):
    """Client for running inference on deployed models."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 30,  # Increased timeout for inference operations
    ):
        """Initialize the InferenceClient.

        Args:
            base_url (str, optional): The base URL of the ModelHub API. Defaults to None.
            client_id (str, optional): The client ID for authentication. Defaults to None.
            client_secret (str, optional): The client secret for authentication. Defaults to None.
            token (str, optional): The token for authentication. Defaults to None.
            timeout (int, optional): Request timeout in seconds. Defaults to 30.
        """
        super().__init__(base_url, client_id, client_secret, token, timeout)
        logger.info("Initialized InferenceClient with base URL: %s", self.base_url)

    def run_text_inference(
        self, model_name: str, text: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run text-based inference on a deployed model.

        Args:
            model_name (str): The name of the model to use for inference.
            text (str): The text input for the model.
            parameters (Dict[str, Any], optional): Additional parameters for inference. Defaults to None.

        Returns:
            Dict[str, Any]: The inference results.

        Raises:
            ModelHubException: If the inference request fails.
        """
        logger.info("Running text inference on model: %s", model_name)

        payload = {"text": text, "parameters": parameters or {}}

        try:
            endpoint = f"model-card/{model_name}/predict"
            response = self.post(endpoint, json=payload)
            logger.debug("Text inference completed successfully")
            return response
        except requests.exceptions.RequestException as e:
            error_msg = f"Text inference failed: {str(e)}"
            logger.error(error_msg)
            raise ModelHubException(error_msg) from e

    def _is_url(self, file_path: str) -> bool:
        """Check if a path is a URL.

        Args:
            file_path (str): The file path to check

        Returns:
            bool: True if the path is a URL, False otherwise
        """
        return file_path.startswith(
            ("http://", "https://", "s3://", "wasbs://", "azure://")
        )

    def _process_file(
        self,
        file_path: Union[str, BinaryIO],
        file_name: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Tuple[str, bytes, str]:
        """Process a file and return its name, content and content type.

        Args:
            file_path (Union[str, BinaryIO]): The file path, URL or file-like object
            file_name (Optional[str]): The filename to use (required for file objects)
            content_type (Optional[str]): The content type (will be guessed if not provided)

        Returns:
            Tuple[str, bytes, str]: A tuple of (filename, file content, content type)

        Raises:
            ModelHubException: If there are errors processing the file
        """
        # Handle string paths (local files or URLs)
        if isinstance(file_path, str):
            if self._is_url(file_path):
                logger.debug("Handling URL as file source: %s", file_path)
                # Extract filename from URL if not provided
                if not file_name:
                    parsed_url = urlparse(file_path)
                    basename = os.path.basename(parsed_url.path)
                    file_name = basename if basename else "file"

                # Download the file content
                # For http/https URLs, use requests
                if file_path.startswith(("http://", "https://")):
                    try:
                        download_response = requests.get(
                            file_path, timeout=self.timeout, stream=True
                        )
                        download_response.raise_for_status()
                        file_content = download_response.content
                        # Try to get content type from response
                        if (
                            not content_type
                            and "Content-Type" in download_response.headers
                        ):
                            content_type = download_response.headers["Content-Type"]
                    except requests.exceptions.RequestException as e:
                        raise ModelHubException(
                            f"Failed to download file from URL: {e}"
                        ) from e
                # For other URL schemes
                else:
                    raise ModelHubException(
                        f"Unsupported URL scheme in {file_path}. Currently supported: http://, https://"
                    )
            else:
                # Local file path
                if not os.path.exists(file_path):
                    raise ModelHubException(f"File not found: {file_path}")
                file_name = file_name or os.path.basename(file_path)
                with open(file_path, "rb") as f:
                    file_content = f.read()
        else:
            # File-like object
            if not file_name:
                raise ModelHubException(
                    "file_name is required when file_path is a file-like object"
                )
            file_content = file_path.read() if hasattr(file_path, "read") else file_path

        # Determine content type if not provided
        if not content_type:
            content_type = (
                mimetypes.guess_type(file_name)[0] or "application/octet-stream"
            )

        return file_name, file_content, content_type

    def run_file_inference(
        self,
        model_name: str,
        file_path: Union[str, BinaryIO],
        file_name: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run file-based inference on a deployed model.

        Args:
            model_name (str): The name of the model to use for inference.
            file_path (Union[str, BinaryIO]): The path to the file, \
            a file-like object, or a URL (http/https/s3/azure).
            file_name (str, optional): The name of the file. \
            Required if file_path is a file-like object. Defaults to None.
            content_type (str, optional): The content type of the file. \
            If not provided, it will be guessed. Defaults to None.

        Returns:
            Dict[str, Any]: The inference results.

        Raises:
            ModelHubException: If the inference request fails or file handling errors occur.
        """
        logger.info("Running file inference on model: %s", model_name)

        try:
            # Process the file to get filename, content and type
            file_name, file_content, content_type = self._process_file(
                file_path, file_name, content_type
            )

            # Prepare multipart/form-data request
            files = {"file": (file_name, file_content, content_type)}

            endpoint = f"model-card/{model_name}/predict/file"

            # Use direct requests call with session and retry handling
            url = f"{self.modelhub_url}/{endpoint}"
            response = self.session.post(
                url, headers=self.headers, files=files, timeout=self.timeout
            )

            result = handle_response(response)
            logger.debug("File inference completed successfully")
            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"File inference failed: {str(e)}"
            logger.error(error_msg)
            raise ModelHubException(error_msg) from e
        except Exception as e:
            error_msg = f"File inference error: {str(e)}"
            logger.error(error_msg)
            raise ModelHubException(error_msg) from e
