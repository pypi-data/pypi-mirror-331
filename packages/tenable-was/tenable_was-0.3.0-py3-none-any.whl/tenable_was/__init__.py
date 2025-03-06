from typing import Optional, Dict, Any, Tuple
import time
import logging
import requests

logger = logging.getLogger(__name__)


class TenableClient:
    """Client for interacting with the Tenable Web Application Scanning API."""

    def __init__(self, access_key: str = "", secret_key: str = "", base_url: str = "https://fedcloud.tenable.com"):
        """
        Initialize the Tenable client.

        Args:
            access_key: The Tenable API access key
            secret_key: The Tenable API secret key
            base_url: The base URL for the Tenable API
        """
        self.base_url = base_url
        self.access_key = access_key
        self.secret_key = secret_key

    @property
    def headers(self) -> Dict[str, str]:
        """
        Get the current headers with up-to-date API keys.

        Returns:
            Dictionary containing the request headers
        """
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "x-apikeys": f"accessKey={self.access_key};secretKey={self.secret_key}",
        }

    def validate_credentials(self) -> None:
        """Validate that credentials are set."""
        if not self.access_key or not self.secret_key:
            raise ValueError("Access key and secret key must be set.")

    def search_configs(self, limit: int = 10, offset: int = 0, sort: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for scan configurations.

        Args:
            limit: Maximum number of results to return
            offset: Offset for pagination
            sort: Field and direction to sort results

        Returns:
            JSON response from the API
        """
        self.validate_credentials()

        query_params = {"limit": limit}

        if offset:
            query_params["offset"] = offset

        if sort:
            query_params["sort"] = sort

        url = f"{self.base_url}/was/v2/configs/search"

        response = requests.post(
            url,
            headers=self.headers,
            params=query_params,
            json={
                "AND": [
                    {"field": "folder_name", "operator": "nmatch", "value": "trash"},
                    {"field": "folder_name", "operator": "nmatch", "value": "_remediation"},
                ]
            },
        )

        return response.json()

    def search_scans(
        self, config_id: str, limit: int = 10, offset: int = 0, sort: Optional[str] = "finalized_at:desc"
    ) -> Dict[str, Any]:
        """
        Search for scans associated with a configuration.

        Args:
            config_id: ID of the configuration
            limit: Maximum number of results to return
            offset: Offset for pagination
            sort: Field and direction to sort results

        Returns:
            JSON response from the API
        """
        self.validate_credentials()

        query_params = {"limit": limit}

        if offset:
            query_params["offset"] = offset

        if sort:
            query_params["sort"] = sort

        url = f"{self.base_url}/was/v2/configs/{config_id}/scans/search"

        response = requests.post(
            url,
            headers=self.headers,
            params=query_params,
            json={"field": "status", "operator": "eq", "value": "completed"},
        )

        return response.json()

    def export_scan(self, scan_id: str, content_type: str = "application/json") -> Any:
        """
        Export a scan report.

        Args:
            scan_id: ID of the scan to export
            content_type: Content type of the report

        Returns:
            Report content (JSON or binary depending on content_type)
        """
        self.validate_credentials()

        url = f"{self.base_url}/was/v2/scans/{scan_id}/report"

        # Initiate report generation
        headers = self.headers
        response = requests.put(
            url,
            headers=headers,
            json={"content-type": content_type},
        )

        if response.status_code == 200:
            logger.info("Report is ready!")
        elif response.status_code == 202:
            logger.info("Report is being generated...")
        elif response.status_code == 400:
            logger.error(f"Invalid scan UUID: {scan_id}")
            return None
        elif response.status_code == 415:
            logger.error(f"Invalid content type: {content_type}")
            return None
        elif response.status_code == 429:
            logger.error("Rate limit exceeded, try again later.")
            return None

        # Sleep for 1 second
        time.sleep(1)

        def download_report() -> Tuple[int, Any]:
            """Helper function to download the report."""
            download_response = requests.get(
                url,
                headers=self.headers,
            )

            if download_response.status_code == 429:
                logger.error("Rate limit exceeded...")
                return download_response.status_code, None
            elif download_response.status_code == 200:
                if content_type == "application/json":
                    return download_response.status_code, download_response.json()
                else:
                    return download_response.status_code, download_response.content

            return download_response.status_code, None

        # Try to download the report up to 5 times
        for attempt in range(5):
            status_code, result = download_report()

            if status_code == 200:
                return result
            elif status_code == 202:
                logger.info("Report is still being generated...")
                time.sleep(attempt * 2)
            else:
                logger.error(f"Failed to download report: {status_code}")
                break

        return None
