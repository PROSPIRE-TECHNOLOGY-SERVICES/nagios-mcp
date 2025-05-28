import json
import os
from typing import Dict, Optional

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

NAGIOS_URL = os.environ.get("NAGIOS_URL")
NAGIOS_USER = os.environ.get("NAGIOS_USER")
NAGIOS_PASS = os.environ.get("NAGIOS_PASS")

if NAGIOS_URL is not None and NAGIOS_URL.endswith("/"):
    cgi_url = f"{NAGIOS_URL}" + "cgi-bin/"
else:
    cgi_url = f"{NAGIOS_URL}" + "/cgi-bin/"
auth = HTTPBasicAuth(NAGIOS_USER, NAGIOS_PASS)
session = requests.Session()
session.auth = auth
common_format_options = "whitespace+enumerate+bitmask+duration"


def make_request(cgi_script: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """
    Helper function to make requests to Nagios Core CGI
    """
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
