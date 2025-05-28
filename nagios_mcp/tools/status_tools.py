import json
from typing import Dict, List, Optional

from .utils import make_request


def get_host_status_fn(
    host_name: Optional[str] = None,
    host_status_filter: Optional[List] = None,
    host_group_filter: Optional[List] = None,
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


def get_service_status_fn(
    host_name: Optional[str] = None,
    service_description: Optional[str] = None,
    service_status_filter: Optional[List] = None,
    host_group_filter: Optional[List] = None,
    service_group_filter: Optional[List] = None,
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


def get_alerts_fn() -> Dict:
    """
    Retrieves current problematic host and service states (alerts).

    Returns:
        - dict {"host": problem_hosts_data, "services": problem_services_data}
    """
    alerts = {"hosts": None, "services": None}
    alerts["hosts"] = get_host_status_fn(host_status_filter=["down", "unreachable"])
    alerts["services"] = get_service_status_fn(
        service_status_filter=["warning", "critical", "unknown"]
    )
    return alerts


def get_nagios_process_info_fn() -> Optional[Dict]:
    """
    Retrieves the Nagios Core program status from statusjson.cgi

    Returns:
        - dict: Parsed JSON response
    """
    params = {"query": "programstatus"}
    data = make_request("statusjson.cgi", params=params)
    return data.get("programstatus") if data else None


def get_hosts_in_group_status_fn(
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
    return get_host_status_fn(
        host_group_filter=[host_group_name], host_status_filter=host_status_filter
    )


def get_services_in_group_status_fn(
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
    return get_service_status_fn(
        service_group_filter=[service_group_name],
        service_status_filter=service_status_filter,
    )


def get_services_on_host_in_group_status_fn(
    host_group_name: str, host_name: str, service_status_filter: Optional[List] = None
) -> Optional[Dict]:
    """
    Retrieves status for all the servies with a specific host group.

    Returns:
        - dict: Parsed JSON response
    """
    return get_service_status_fn(
        host_name=host_name,
        host_group_filter=[host_group_name],
        service_status_filter=service_status_filter,
    )


def get_overall_health_summary_fn() -> Dict:
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


def get_unhandled_problems_fn(problem_type: str = "all") -> Dict:
    """
    Retrieves all the unhandled problems for all the hosts and services.

    Args:
        - problem_type (str): ["all", "host", "service"]
    Returns:
        - dict: Parsed JSON response
    """
    unhandled = {"hosts": [], "services": []}
    if problem_type == "all" or problem_type == "host":
        hosts = get_host_status_fn(host_status_filter=["down", "unreachable"])
        if hosts:
            for hostname, h_data in hosts.items():
                if (
                    not h_data.get("problem_has_been_acknowledged")
                    and h_data.get("scheduled_downtime_depth", 0) == 0
                ):
                    unhandled["hosts"].append({hostname: h_data})

    if problem_type == "all" or problem_type == "service":
        services = get_service_status_fn(
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


if __name__ == "__main__":
    print("--- Nagios Program Status ---")
    program_status = get_nagios_process_info_fn()
    if program_status:
        print(json.dumps(program_status, indent=2))
    else:
        print("Could not retrieve Nagios program status.")
    print("\n")

    print("--- All Host Status ---")
    all_hosts_status = get_host_status_fn()
    if all_hosts_status:
        for host_name, status_data in all_hosts_status.items():
            print(f"Host: {host_name}, Status: {status_data.get('status', 'N/A')}")
    else:
        print("Could not retrieve all host statuses.")
    print("\n")

    print("--- Specific Host Status (e.g., localhost) ---")
    # Replace 'localhost' with a host defined in your Nagios
    lh_status = get_host_status_fn(host_name="localhost")
    if lh_status:
        print(json.dumps(lh_status, indent=2))
    else:
        print("Could not retrieve status for host 'localhost'.")
    print("\n")

    print("--- All Service Status ---")
    all_services_status = get_service_status_fn()
    if all_services_status:
        for host_name, services in all_services_status.items():
            for service_desc, status_data in services.items():
                print(
                    f"Host: {host_name}, Service: {service_desc}, Status: {status_data.get('status', 'N/A')}"
                )
    else:
        print("Could not retrieve all service statuses.")
    print("\n")

    print("--- Specific Service Status (e.g., SSH on localhost) ---")
    # Replace 'localhost' and 'SSH' with actual host/service
    ping_status = get_service_status_fn(
        host_name="localhost", service_description="SSH"
    )
    if ping_status:
        print(json.dumps(ping_status, indent=2))
    else:
        print("Could not retrieve SSH service status on localhost.")
    print("\n")

    print("--- Current Alerts (Problems) ---")
    alerts = get_alerts_fn()
    print("Problem Hosts:")
    if alerts.get("hosts"):
        for host_name, host_data in alerts["hosts"].items():
            print(
                f"  Host: {host_name}, Status: {host_data.get('status')}, Output: {host_data.get('plugin_output')}"
            )
    else:
        print("  No problem hosts found or error retrieving.")
    print("Problem Services:")
    if alerts.get("services"):
        for host_name, services in alerts["services"].items():
            for service_desc, service_data in services.items():
                print(
                    f"  Host: {host_name}, Service: {service_desc}, Status: {service_data.get('status')}, Output: {service_data.get('plugin_output')}"
                )
    else:
        print("  No problem services found or error retrieving.")
    print("\n")

    print("--- Status of Hosts in Group 'linux-servers' ---")
    # Replace 'linux-servers' with an actual hostgroup name
    hosts_in_group = get_hosts_in_group_status_fn("linux-servers")
    if hosts_in_group:
        for host_name, status_data in hosts_in_group.items():
            print(
                f"Host in Group: {host_name}, Status: {status_data.get('status', 'N/A')}"
            )
    else:
        print("Could not retrieve status for hosts in group 'linux-servers'.")
    print("\n")
