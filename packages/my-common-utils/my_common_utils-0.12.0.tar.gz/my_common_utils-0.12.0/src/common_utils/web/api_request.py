import requests
import json


def get_request(url, headers=None, catch_exception=False) -> dict | None:
    """
    Send a POST request to the given URL with the given data and headers.
    """
    if headers is None:
        headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        if catch_exception:
            return None
        else:
            raise Exception(f"Error sending POST request to {url}: {e}")



def post_request(url, data, headers=None, catch_exception=False) -> dict | None:
    """
    Send a POST request to the given URL with the given data and headers.
    """
    if headers is None:
        headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response.json()
    except Exception as e:
        if catch_exception:
            return None
        else:
            raise Exception(f"Error sending POST request to {url}: {e}")
