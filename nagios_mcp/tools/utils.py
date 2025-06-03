import json
from typing import Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

NAGIOS_URL = None
NAGIOS_USER = None
NAGIOS_PASS = None
cgi_url = None
auth = None
session = None
common_format_options = "whitespace+enumerate+bitmask+duration"


def initialize_nagios_config(nagios_url: str, nagios_user: str, nagios_pass: str):
    """Initialize Nagios Configuration from provided parameters"""
    global NAGIOS_URL, NAGIOS_USER, NAGIOS_PASS, cgi_url, auth, session

    NAGIOS_URL = nagios_url
    NAGIOS_USER = nagios_user
    NAGIOS_PASS = nagios_pass

    if NAGIOS_URL is not None and NAGIOS_URL.endswith("/"):
        cgi_url = f"{NAGIOS_URL}" + "cgi-bin/"
    else:
        cgi_url = f"{NAGIOS_URL}" + "/cgi-bin/"

    auth = HTTPBasicAuth(NAGIOS_USER, NAGIOS_PASS)
    session = requests.session()
    session.auth = auth

def _check_config():
    """Check if configuration has been initialized"""
    if NAGIOS_URL is None or NAGIOS_USER is None or NAGIOS_PASS is None:
        raise RuntimeError(
            "Nagios configuration not initlilized",
            "Make sure to run the server with a valid config file."
        )

def make_request(cgi_script: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """
    Helper function to make requests to Nagios Core CGI
    """
    _check_config() # ensure config is initialized
    if params is None:
        params = {}

    if "details" not in params and (
        cgi_script == "statusjson.cgi" or cgi_script == "objectjson.cgi"
    ):
        if params.get("query", {}).endswith("list"):
            params["details"] = "true"

    url = f"{cgi_url}{cgi_script}"
    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()  # For HTTP errors
        response_json = response.json()

        if response_json.get("result", {}).get("type_code") == 0:  # Success
            return response_json.get("data", {})
        else:
            error_message = response_json.get("result", {}).get(
                "message", "Unknown CGI Error"
            )
            print(
                f"CGI Error for {cgi_script} with query '{params.get('query')}': {error_message}"
            )
            print(f"Full response for debug: {json.dumps(response_json, indent=2)}")
            return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} for URL: {e.response.url}")
        print(f"Response Text: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request Failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response text (if available): {e.response.text}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
    return None
