"""local api client used to obtain
IoT service credentials for iot mqtt communication

"""

import os
import logging
import time
import requests

API_APPS_CONFIG_URL = "http://localhost:{}/api/apps"
API_DEVICE_CONFIG_URL = "http://localhost:{}/api/device"

MAX_RETRIES = 5
RETRY_DELAY = 1  # seconds


def get_app_config_api(appId, port=5000):
    """get app configuration from local HTTP server"""
    return local_http_api(
        API_APPS_CONFIG_URL, query_param={"applicationId": appId}, port=port
    )


def get_device_config_api(port=5000):
    """get app configuration from local HTTP server"""
    return local_http_api(API_DEVICE_CONFIG_URL, port=port)


def local_http_api(url, query_param=None, port=5000):
    """local HTTP server API"""
    env_port = os.getenv("PORT")
    if env_port:
        port = env_port
    # add retry logic
    for attempt in range(MAX_RETRIES):
        try:
            result = requests.get(url.format(port), params=query_param, timeout=30)
            result.raise_for_status()
            if result.status_code == 200:
                data = result.json()
                logging.info(
                    f"{__name__}: signalsdk:HTTP request "
                    f"local HTTP server success. Data: {data}"
                )
                return data
            raise Exception(
                f"local HTTP request failed. Status code: {result.status_code}"
            )
        except Exception as e:
            logging.error(
                f"{__name__}: signalsdk:HTTP request attempt {attempt + 1} of {MAX_RETRIES}"
                f"local HTTP server failed. Error: {e}"
            )
            # exponential backoff
            time.sleep(RETRY_DELAY + attempt * 2)
    logging.error(
        f"{__name__}: signalsdk:HTTP request "
        f"local HTTP server failed after {MAX_RETRIES} attempts"
    )
    return None
