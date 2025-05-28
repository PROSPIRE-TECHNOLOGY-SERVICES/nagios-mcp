import json
from typing import Dict, Optional

from .utils import make_request


def get_object_list_config_fn(object_type_plural: str) -> Optional[Dict]:
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


def get_single_object_config_fn(
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


def get_host_dependencies_fn(
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


def get_service_dependencies_fn(
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


def get_contacts_for_object_fn(
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
    config = get_single_object_config_fn(object_type, object_name, service_description)
    if not config:
        return None

    contact_info = {"contacts": [], "contact_groups": []}
    if "contacts" in config:
        for cn in config["contacts"]:
            contact_details = get_single_object_config_fn("contact", cn)
            if contact_details:
                contact_info["contacts"].append(contact_details)
    if "contact_groups" in config:
        for cgn in config["contact_groups"]:
            cg_details = get_single_object_config_fn("contactgroup", cgn)
            if cg_details:
                contact_info["contact_groups"].append(cg_details)

    return contact_info


def get_comments_fn(
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


def get_comment_by_id_fn(comment_id: str) -> Optional[Dict]:
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


def get_downtimes_fn(
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


if __name__ == "__main__":
    print("--- Configuration for ALL Hostgroups ---")
    hg_configs = get_object_list_config_fn("hostgroups")
    if hg_configs:
        for hg_name, config in hg_configs.items():
            print(f"Hostgroup Config: {hg_name}, Alias: {config.get('alias', 'N/A')}")
    else:
        print("Could not retrieve hostgroup configurations.")
    print("\n")

    print("--- Configuration for a SPECIFIC Hostgroup (e.g., 'linux-servers') ---")
    # Replace 'linux-servers' with an actual hostgroup name
    specific_hg_config = get_single_object_config_fn("hostgroup", "linux-servers")
    if specific_hg_config:
        print(json.dumps(specific_hg_config, indent=2))
    else:
        print("Could not retrieve specific hostgroup config for 'linux-servers'.")
    print("\n")

    # Add more examples for service groups, contacts, etc. as needed.
    print("--- Configuration for ALL Services ---")
    all_service_configs = get_object_list_config_fn("services")
    if all_service_configs:
        # This can be very verbose
        print(
            f"Retrieved {len(all_service_configs)} service configurations. Example for one host if present:"
        )
        example_host = next(iter(all_service_configs)) if all_service_configs else None
        if example_host:
            for service_desc, config in all_service_configs[example_host].items():
                print(
                    f"  Config for {example_host} - {service_desc}: Check command: {config.get('check_command')}"
                )
                break  # Just show one service from one host
    else:
        print("Could not retrieve all service configurations.")
