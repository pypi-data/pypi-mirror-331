from typing import Optional
import time
import logging

import requests

logger = logging.getLogger(__name__)

_base_url = "https://fedcloud.tenable.com"
accessKey = ""
secretKey = ""

_default_headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-apikeys": f"accessKey={accessKey};secretKey={secretKey}",
}


def search_configs(limit=10, offset=0, sort: Optional[str] = None):
    if accessKey == "" or secretKey == "":
        raise ValueError("Access key and secret key must be set.")

    query_params = {"limit": limit}

    if offset:
        query_params["offset"] = offset

    if sort:
        query_params["sort"] = sort

    url = f"{_base_url}/was/v2/configs/search"

    response = requests.post(
        url,
        headers=_default_headers,
        params=query_params,
        json={
            "AND": [
                {"field": "folder_name", "operator": "nmatch", "value": "trash"},
                {"field": "folder_name", "operator": "nmatch", "value": "_remediation"},
            ]
        },
    )

    json_result = response.json()
    return json_result


def search_scans(config_id: str, limit=10, offset=0, sort: Optional[str] = "finalized_at:desc"):
    if accessKey == "" or secretKey == "":
        raise ValueError("Access key and secret key must be set.")

    query_params = {"limit": limit}

    if offset:
        query_params["offset"] = offset

    if sort:
        query_params["sort"] = sort

    url = f"{_base_url}/was/v2/configs/{config_id}/scans/search"

    response = requests.post(
        url,
        headers=_default_headers,
        params=query_params,
        json={"field": "status", "operator": "eq", "value": "completed"},
    )

    json_result = response.json()
    return json_result


def export_scan(scan_id: str, content_type="application/json"):
    if accessKey == "" or secretKey == "":
        raise ValueError("Access key and secret key must be set.")

    url = f"{_base_url}/was/v2/scans/{scan_id}/report"

    response = requests.put(
        url,
        headers=_default_headers,
        json={**_default_headers, "content-type": content_type},
    )

    if response.status_code == 200:
        logger.info("Report is ready!")
    elif response.status_code == 202:
        logger.info("Report is being generated...")
    elif response.status_code == 400:
        logger.error(f"Invalid scan UUID: {scan_id}")
    elif response.status_code == 415:
        logger.error(f"Invalid content type: {content_type}")
    elif response.status_code == 429:
        logger.error("Rate limit exceeded, try again later.")

    # Sleep for 1 second
    time.sleep(1)

    def download_report():
        download_response = requests.get(
            url,
            headers=_default_headers,
        )

        if download_response.status_code == 429:
            logger.error("Rate limit exceeded...")
            return download_response.status_code, None
        elif download_response.status_code == 200:
            if content_type == "application/json":
                json_result = download_response.json()
                return download_response.status_code, json_result
            else:
                return download_response.status_code, download_response.content

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
