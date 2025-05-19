import os
from dotenv import load_dotenv
from typing import Optional, Dict, List

import json
import requests
from requests.auth import HTTPBasicAuth
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("NagiosMCP")

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


# ------------------- STATUS TOOLS ---------------------


@mcp.tool()
def get_host_status(
    host_name: Optional[str] = None,
    host_status_filter: Optional[List | str] = None,
    host_group_filter: Optional[List | str] = None,
) -> Optional[Dict]:
    """
    Retrieves status for all hosts or a specific host.

    Args:
        - host_name (str, optional): Specific host to get status for.
                                    If None, gets status for all hosts (hostlist).
        - host_status_filter (list, optional): List of host statuses to filter by
                                             (e.g., ["down", "unreachable"]).
        - host_group_filter (list, optional): List of host groups to filter by.
    Returns:
        - dict or None: Parsed JSON data (e.g., content of "hostlist" or "host")
    """
    params = {}
    if host_name:
        params["query"] = "host"
        params["hostname"] = host_name
    else:
        params["query"] = "hostlist"

    if host_status_filter and isinstance(host_status_filter, list):
        params["hoststatus"] = " ".join(host_status_filter)  # space separated
    if host_group_filter:
        params["hostgroup"] = host_group_filter

    data = make_request("statusjson.cgi", params=params)
    if data:
        if host_name:
            return data.get("host")
        return data.get("hostlist")
    return None


@mcp.tool()
def get_service_status(
    host_name: Optional[str] = None,
    service_description: Optional[str] = None,
    service_status_filter: Optional[List | str] = None,
    host_group_filter: Optional[List | str] = None,
    service_group_filter: Optional[List | str] = None,
) -> Optional[Dict]:
    """
    Retrieves status for services using statusjson.cgi.

    Args:
        - host_name (str, optional): Hostname to filter services by.
        - service_description (str, optional): Specific service description.
                                                If provided with host_name, gets status for a single service.
        - service_status_filter (list, optional): List of service statuses to filter by
                                                    (e.g., ["warning", "critical", "unknown"])
        - host_group_filter (list, optional): List of host groups to filter by.
        - service_group_filter (list, optional): List of service groups to filter by.
    Returns:
        - dict or None: Parsed JSON data (e.g., content of "servicelist" or "service")
    """
    params = {}
    if host_name and service_description:
        params["query"] = "service"
        params["hostname"] = host_name
        params["servicedescription"] = service_description
    else:
        params["query"] = "servicelist"
        if host_name:
            params["hostname"] = host_name  # Filter servicelist by host

    if service_status_filter and isinstance(service_status_filter, list):
        params["servicestatus"] = " ".join(service_status_filter)
    if host_group_filter:
        params["hostgroup"] = host_group_filter
    if service_group_filter:
        params["servicegroup"] = service_group_filter

    data = make_request("statusjson.cgi", params=params)
    if data:
        if host_name and service_description:
            return data.get("service")
        return data.get("servicelist")
    return None


@mcp.tool()
def get_alerts() -> Dict:
    """
    Retrieves current problematic host and service states (alerts).

    Returns:
        - dict {"host": problem_hosts_data, "services": problem_services_data}
    """
    alerts = {"hosts": None, "services": None}
    alerts["hosts"] = get_host_status(host_status_filter=["down", "unreachable"])
    alerts["services"] = get_service_status(
        service_status_filter=["warning", "critical", "unknown"]
    )
    return alerts


@mcp.tool()
def get_program_status() -> Optional[Dict]:
    """
    Retrieves the Nagios Core program status from statusjson.cgi

    Returns:
        - dict: Parsed JSON response
    """
    params = {"query": "programstatus"}
    data = make_request("statusjson.cgi", params=params)
    return data.get("programstatus") if data else None


@mcp.tool()
def get_hosts_in_group_status(
    host_group_name: str, host_status_filter: Optional[List] = None
) -> Optional[Dict]:
    """
    Retrieves status for all hosts within a specific host group.

    Args:
        - host_group_name (str): The name of the host group.
        - host_status_filter (list, optional): Filter by host statuses.
    Returns:
        - dict or None: Data for hosts in the group, typically from "hostlist".
    """
    return get_host_status(
        host_group_filter=host_group_name, host_status_filter=host_status_filter
    )


@mcp.tool()
def get_services_in_group_status(
    service_group_name: str, service_status_filter: Optional[List] = None
) -> Optional[Dict]:
    """
    Retrieves status for all services within a specific service group.

    Args:
        - service_group_name (str): The name of the service group.
        - service_status_filter (list, optional): Filter by service statuses.
    Returns:
        - dict or None: Data for servies in the group, typically from "servicelist".
    """
    return get_service_status(
        service_group_filter=service_group_name,
        service_status_filter=service_status_filter,
    )


@mcp.tool()
def get_services_on_host_in_group_status(
    host_group_name: str, host_name: str, service_status_filter: Optional[List] = None
) -> Optional[Dict]:
    """
    Retrieves status for all the servies with a specific host group.

    Returns:
        - dict: Parsed JSON response
    """
    return get_service_status(
        host_name=host_name,
        host_group_filter=host_group_name,
        service_status_filter=service_status_filter,
    )


@mcp.tool()
def get_overall_health_summary() -> Dict:
    """
    Retrieves overall health summary for all the hosts and services.

    Returns:
        - (dict or None): Parsed JSON data
    """
    summary = {"host_counts": None, "service_counts": None}
    host_data = make_request("statusjson.cgi", params={"query": "hostcount"})
    if host_data:
        summary["host_counts"] = host_data.get("hostcount")
    service_data = make_request("statusjson.cgi", params={"query": "servicecount"})
    if service_data:
        summary["service_counts"] = service_data.get("servicecount")
    return summary


@mcp.tool()
def get_unhandled_problems(problem_type: str = "all") -> Dict:
    """
    Retrieves all the unhandled problems for all the hosts and services.

    Args:
        - problem_type (str): ["all", "host", "service"]
    Returns:
        - dict: Parsed JSON response
    """
    unhandled = {"hosts": [], "services": []}
    if problem_type == "all" or problem_type == "host":
        hosts = get_host_status(host_status_filter=["down", "unreachable"])
        if hosts:
            for hostname, h_data in hosts.items():
                if (
                    not h_data.get("problem_has_been_acknowledged")
                    and h_data.get("scheduled_downtime_depth", 0) == 0
                ):
                    unhandled["hosts"].append({hostname: h_data})

    if problem_type == "all" or problem_type == "service":
        services = get_service_status(
            service_status_filter=["warning", "critical", "unknown"]
        )
        if services:
            for hostname, s_dict in services.items():
                for service_desc, s_data in s_dict.items():
                    if (
                        s_data.get("problem_has_been_acknowledged")
                        and s_data.get("scheduled_downtime_depth", 0) == 0
                    ):
                        unhandled["services"].append({hostname: {service_desc: s_data}})

    return unhandled


# ------------------- CONFIG TOOLS ---------------------


@mcp.tool()
def get_object_list_config(object_type_plural: str) -> Optional[Dict]:
    """
    Retrieves configuration list for object types like "hosts", "services", "hostgroups", etc.

    Args:
        - object_type_plural (str): Plural type of object (e.g., "hosts", "services", "hostgroups").
                                    This will be used to form the query (e.g., "hostlist", "servicelist")
    Returns:
        - dict or None: Parsed JSON data (e.g., content of "hostlist", "servicelist")
    """
    query_map = {
        "hosts": "hostlist",
        "services": "servicelist",
        "hostgroups": "hostgrouplist",
        "servicegroups": "servicegrouplist",
        "contacts": "contactlist",
        "contactgroups": "contactgrouplist",
        "timeperiods": "timeperiodlist",
        "commands": "commandlist",
    }
    if object_type_plural.lower() not in query_map:
        print(
            f"Error: Unsupported object_type_plural for listing: {object_type_plural}"
        )
        return None

    params = {"query": query_map[object_type_plural.lower()]}
    data = make_request("objectjson.cgi", params=params)
    return data.get(query_map[object_type_plural.lower()]) if data else None


@mcp.tool()
def get_single_object_config(
    object_type_singular: str,
    object_name: str,
    service_description_for_service: Optional[str] = None,
) -> Optional[Dict]:
    """
    Retrieves configuration for a single specific object.

    Args:
        - object_type_singular (str): Singular type of object (e.g., "host", "service", "hostgroup")
        - object_name (str): Name of the specific object. For "service", this is the hostname.
        - service_description_for_service (str, optional): Required if object_type_singular is "service".
    Returns:
        - dict or None: Parsed JSON data for the single object.
    """
    params = {"query": object_type_singular.lower()}

    type_lower = object_type_singular.lower()
    if type_lower == "host":
        params["hostname"] = object_name
    elif type_lower == "service":
        if not service_description_for_service:
            print(
                "Error: For 'service' config, service_description_for_service is required."
            )
            return None
        params["hostname"] = object_name
        params["servicedescription"] = service_description_for_service
    elif type_lower == "hostgroup":
        params["hostgroup"] = object_name
    elif type_lower == "servicegroup":
        params["servicegroup"] = object_name
    elif type_lower == "contact":
        params["contactname"] = object_name
    elif type_lower == "contactgroup":
        params["contactgroup"] = object_name
    elif type_lower == "timeperiod":
        params["timeperiod"] = object_name
    elif type_lower == "command":
        params["command"] = object_name
    else:
        print(
            f"Error: Specific object retrieval for type '{object_type_singular}' "
            "needs explicit parameter mapping or is not supported by this simplified method."
        )
        return None

    data = make_request("objectjson.cgi", params=params)
    return data.get(type_lower) if data else None


@mcp.tool()
def get_host_dependencies(
    host_name: Optional[str] = None,
    master_host: Optional[str] = None,
    dependent_host: Optional[str] = None,
) -> Optional[Dict]:
    """
    Retrieves host dependencies for the given host.

    Args:
        - host_name (str, optional): Name of host
        - master_name (str, optional): Name of the master host
        - dependent_host (str, optional): Name of the dependent host
    Returns:
        - dict: Structed list of the host dependencies
    """
    params = {"query": "hostdependencylist"}
    if host_name:
        params["dependenthostname"] = host_name
    if master_host:
        params["masterhostname"] = master_host
    if dependent_host and not host_name:
        params["dependenthostname"] = dependent_host
    return make_request("statusjson.cgi", params=params)


@mcp.tool()
def get_service_dependencies(
    host_name: Optional[str] = None,
    service_description: Optional[str] = None,
    master_host: Optional[str] = None,
    master_service_description: Optional[str] = None,
) -> Optional[Dict]:
    """
    Retrieves service dependencies for the given host.

    Args:
        - host_name (str, optional): Name of the host
        - service_description (str, optional): Description of the service of the host
        - master_host (str, optional): Name of the master host
        - master_service_description (str, optional): Description of the service of the master host

    Returns:
        - (str): Structed output of the Service Dependency list of the host
    """
    params = {"query": "servicedependencylist"}
    if host_name:
        params["dependenthostname"] = host_name
    if service_description:
        params["dependentservicedescription"] = service_description
    if master_host:
        params["masterhostname"] = master_host
    if master_service_description:
        params["masterservicedescription"] = master_service_description
    return make_request("statusjson.cgi", params=params)


@mcp.tool()
def get_contacts_for_object(
    object_type: str, object_name: str, service_description: Optional[str] = None
) -> Optional[Dict]:
    """
    Retrieves the list of contacts to inform for an object.

    Args:
        - object_type (str): The type of the Object
        - object_name (str): The object name
        - service_description (str, optional): The description of the service
    Returns:
        - dict: Parsed JSON response
    """
    config = get_single_object_config(object_type, object_name, service_description)
    if not config:
        return None

    contact_info = {"contacts": [], "contact_groups": []}
    if "contacts" in config:
        for cn in config["contacts"]:
            contact_details = get_single_object_config("contact", cn)
            if contact_details:
                contact_info["contacts"].append(contact_details)
    if "contact_groups" in config:
        for cgn in config["contact_groups"]:
            cg_details = get_single_object_config("contactgroup", cgn)
            if cg_details:
                contact_info["contact_groups"].append(cg_details)

    return contact_info


@mcp.tool()
def get_comments(
    host_name: Optional[str] = None,
    service_description: Optional[str] = None,
    limit: int = 50,
) -> Optional[Dict]:
    """
    Retrieves comments based on the host and service.

    Args:
        - host_name (str, optional): The name of the host
        - service_description (str, optional): The description of the service
        - limit (int, default=50): The maximum number of comments to fetch
    Returns:
        - dict: Parsed JSON response
    """
    params = {"query": "commentlist", "count": limit}
    if host_name:
        params["hostname"] = host_name
    if service_description:
        params["servicedescription"] = service_description
    data = make_request("statusjson.cgi", params=params)
    return data.get("commentlist") if data else None


@mcp.tool()
def get_comment_by_id(comment_id: str) -> Optional[Dict]:
    """
    Retrieves comments for the given comment id.

    Args:
        - comment_id (str): The comment_id for the comment to fetch.
    Returns:
        - dict: Parsed JSON response.
    """
    data = make_request(
        "statusjson.cgi", params={"query": "comment", "commentid": comment_id}
    )
    return data.get("comment") if data else None


@mcp.tool()
def get_downtimes(
    host_name: Optional[str] = None,
    service_description: Optional[str] = None,
    active_only: Optional[bool] = None,
    limit: int = 50,
) -> Optional[Dict]:
    """
    Retrieves the information for the downtimes in the Nagios Host Process.

    Args:
        - host_name (str, optional): The name of the host
        - service_description (str, optional): The description of the service.
        - active_only (bool, optional): Whether to fetch only the active downtimes.
        - limit (int, default=50): The maximum number of the downtime logs to fetch.
    Returns:
        - (dict): Parsed JSON response
    """
    params = {"query": "downtimelist", "count": limit}
    if host_name:
        params["hostname"] = host_name
    if service_description:
        params["servicedescription"] = service_description
    if active_only:
        params["ineffect"] = "yes"

    data = make_request("statusjson.cgi", params=params)
    return data.get("downtimelist") if data else None


@mcp.tool()
def get_nagios_process_info() -> Optional[Dict]:
    """
    Returns the information for the Nagios process.
    Alias for get_program_status function.

    Returns:
        - dict: Parsed JSON response.
    """
    return get_program_status()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MCP Server for Nagios")
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "sse"],
        help="Transport Protocol for MCP Server, default=stdio",
    )
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")

    # print("--- Nagios Program Status ---")
    # program_status = get_program_status()
    # if program_status:
    #     print(json.dumps(program_status, indent=2))
    # else:
    #     print("Could not retrieve Nagios program status.")
    # print("\n")
    #
    # print("--- All Host Status ---")
    # all_hosts_status = get_host_status()
    # if all_hosts_status:
    #     for host_name, status_data in all_hosts_status.items():
    #         print(f"Host: {host_name}, Status: {status_data.get('status', 'N/A')}")
    # else:
    #     print("Could not retrieve all host statuses.")
    # print("\n")
    #
    # print("--- Specific Host Status (e.g., localhost) ---")
    # # Replace 'localhost' with a host defined in your Nagios
    # lh_status = get_host_status(host_name="localhost")
    # if lh_status:
    #     print(json.dumps(lh_status, indent=2))
    # else:
    #     print("Could not retrieve status for host 'localhost'.")
    # print("\n")

    # print("--- All Service Status ---")
    # all_services_status = get_service_status()
    # if all_services_status:
    #     for host_name, services in all_services_status.items():
    #         for service_desc, status_data in services.items():
    #             print(f"Host: {host_name}, Service: {service_desc}, Status: {status_data.get('status', 'N/A')}")
    # else:
    #     print("Could not retrieve all service statuses.")
    # print("\n")
    #
    # print("--- Specific Service Status (e.g., SSH on localhost) ---")
    # # Replace 'localhost' and 'SSH' with actual host/service
    # ping_status = get_service_status(host_name="localhost", service_description="SSH")
    # if ping_status:
    #     print(json.dumps(ping_status, indent=2))
    # else:
    #     print("Could not retrieve SSH service status on localhost.")
    # print("\n")
    #
    # print("--- Current Alerts (Problems) ---")
    # alerts = get_alerts()
    # print("Problem Hosts:")
    # if alerts.get('hosts'):
    #     for host_name, host_data in alerts['hosts'].items():
    #         print(f"  Host: {host_name}, Status: {host_data.get('status')}, Output: {host_data.get('plugin_output')}")
    # else:
    #     print("  No problem hosts found or error retrieving.")
    # print("Problem Services:")
    # if alerts.get('services'):
    #     for host_name, services in alerts['services'].items():
    #         for service_desc, service_data in services.items():
    #              print(f"  Host: {host_name}, Service: {service_desc}, Status: {service_data.get('status')}, Output: {service_data.get('plugin_output')}")
    # else:
    #     print("  No problem services found or error retrieving.")
    # print("\n")
    #
    # print("--- Configuration for ALL Hostgroups ---")
    # hg_configs = get_object_list_config('hostgroups')
    # if hg_configs:
    #     for hg_name, config in hg_configs.items():
    #         print(f"Hostgroup Config: {hg_name}, Alias: {config.get('alias', 'N/A')}")
    # else:
    #     print("Could not retrieve hostgroup configurations.")
    # print("\n")
    #
    # print("--- Configuration for a SPECIFIC Hostgroup (e.g., 'linux-servers') ---")
    # # Replace 'linux-servers' with an actual hostgroup name
    # specific_hg_config = get_single_object_config('hostgroup', 'linux-servers')
    # if specific_hg_config:
    #     print(json.dumps(specific_hg_config, indent=2))
    # else:
    #     print("Could not retrieve specific hostgroup config for 'linux-servers'.")
    # print("\n")
    #
    # print("--- Status of Hosts in Group 'linux-servers' ---")
    # # Replace 'linux-servers' with an actual hostgroup name
    # hosts_in_group = get_hosts_in_group_status('linux-servers')
    # if hosts_in_group:
    #     for host_name, status_data in hosts_in_group.items():
    #         print(f"Host in Group: {host_name}, Status: {status_data.get('status', 'N/A')}")
    # else:
    #     print("Could not retrieve status for hosts in group 'linux-servers'.")
    # print("\n")
    #
    # # Add more examples for service groups, contacts, etc. as needed.
    # print("--- Configuration for ALL Services ---")
    # all_service_configs = get_object_list_config('services')
    # if all_service_configs:
    #     # This can be very verbose
    #     print(f"Retrieved {len(all_service_configs)} service configurations. Example for one host if present:")
    #     example_host = next(iter(all_service_configs)) if all_service_configs else None
    #     if example_host:
    #         for service_desc, config in all_service_configs[example_host].items():
    #             print(f"  Config for {example_host} - {service_desc}: Check command: {config.get('check_command')}")
    #             break # Just show one service from one host
    # else:
    #     print("Could not retrieve all service configurations.")
