import logging
import mcp.types as types
from .status_tools import (
    get_host_status_fn,
    get_service_status_fn,
    get_alerts_fn,
    get_nagios_process_info_fn,
    get_hosts_in_group_status_fn,
    get_services_in_group_status_fn,
    get_services_on_host_in_group_status_fn,
    get_overall_health_summary_fn,
    get_unhandled_problems_fn
)
from .config_tools import (
    get_object_list_config_fn,
    get_single_object_config_fn,
    get_host_dependencies_fn,
    get_service_dependencies_fn,
    get_contacts_for_object_fn,
    get_comment_by_id_fn,
    get_comments_fn,
    get_downtimes_fn
)
from typing import List

logger = logging.getLogger("nagios-mcp-server")

# -----------------------------------------------------------------------------
#                                STATUS TOOLS
# -----------------------------------------------------------------------------

get_host_status = types.Tool(
    name="get_host_status",
    description="Retrieves status for all hosts or a specific host",
    inputSchema={
        "type": "object",
        "properties": {
            "host_name": {
                "type": "string",
                "description": "Specific host to get status for"
            },
            "host_status_filter": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of host statuses to filter by, "
                                "(e.g., ['down', 'unreachable'])"
            },
            "host_group_filter": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of host groups to filter by"
            }
        }
    }
)

get_service_status = types.Tool(
    name="get_service_status",
    description="Retrieves status for services using statusjson.cgi",
    inputSchema={
        "type": "object",
        "properties": {
            "host_name": {
                "type": "string",
                "description": "Hostname to filter services by",
            },
            "service_description": {
                "type": "string",
                "description": "Specific service description. If provided with `host_name`, gets status for a single service"
            },
            "service_status_filter": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of service statuses to filter by, (e.g., ['warning', 'critical', 'unknown']"
            },
            "host_group_filter": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of host groups to filter by"
            },
            "service_group_filter": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of service groups to filter by"
            }
        }
    }
)

get_alerts = types.Tool(
    name="get_alerts",
    description="Retrieves current problematic host and service statuses (alerts)",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)

get_nagios_process_info = types.Tool(
    name="get_nagios_process_info",
    description="Retrieves the Nagios Core program status from `statusjson.cgi`",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)

get_hosts_in_group_status = types.Tool(
    name="get_hosts_in_group_status",
    description="Retrieves status for all hosts within a specific host group",
    inputSchema={
        "type": "object",
        "properties": {
            "host_group_name": {
                "type": "string",
                "description": "The name of the host group",
            },
            "host_status_filter": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter for host statuses"
            }
        },
        "required": ["host_group_name"]
    }
)

get_services_in_group_status = types.Tool(
    name="get_services_in_group_status",
    description="Retrieves status for all services within a specific host group",
    inputSchema={
        "type": "object",
        "properties": {
            "service_group_name": {
                "type": "string",
                "description": "The name of the service group",
            },
            "service_status_filter": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter for service statuses"
            }
        },
        "required": ["service_group_name"]
    }
)

get_services_on_host_in_group_status = types.Tool(
    name="get_services_on_host_in_group_status",
    description="Retrieves status for all the services with a specific host group",
    inputSchema={
        "type": "object",
        "properties": {
            "host_group_name": {
                "type": "string",
                "description": "The name of the host group"
            },
            "host_name": {
                "type": "string",
                "description": "The name of the host"
            },
            "service_status_filter": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter for service statuses"
            }
        },
        "required": ["host_group_name", "host_name"]
    }
)

get_overall_health_summary = types.Tool(
    name="get_overall_health_summary",
    description="Retrieves overall health summary for all the hosts and services",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)

get_unhandled_problems = types.Tool(
    name="get_unhandled_problems",
    description="Retrieves all the unhandled problems for all the hosts and services",
    inputSchema={
        "type": "object",
        "properties": {
            "problem_type": {
                "type": "string",
                "description": "Whether to look for host problems or service problems or both, e.g.: ['all', 'host', 'service']",
                "default": "all"
            }
        }
    }
)


# -----------------------------------------------------------------------------
#                                CONFIG TOOLS
# -----------------------------------------------------------------------------

get_object_list_config = types.Tool(
    name="get_object_list_config",
    description="Retrieves configuration list for object like 'hosts', 'services', 'hostgroups', etc.",
    inputSchema={
        "type": "object",
        "properties": {
            "object_type_plural": {
                "type": "string",
                "description": "Plural type of object (e.g., 'hosts', 'services', 'hostgroups'). It will be used to form the query."
            }
        }
    }
)

get_single_object_config = types.Tool(
    name="get_single_object_config",
    description="Retrieves configuration for a single specific object",
    inputSchema={
        "type": "object",
        "properties": {
            "object_type_singular": {
                "type": "string",
                "description": "Singular type of object, (e.g., 'host', 'service', 'hostgroup'"
            },
            "object_name": {
                "type": "string",
                "description": "Name of the specific object. For 'service', this is the hostname."
            },
            "service_description_for_service": {
                "type": "string",
                "description": "Required if `object_type_singular` is 'service'"
            }
        },
        "required": ["object_type_singular", "object_name"]
    }
)

get_host_dependencies = types.Tool(
    name="get_host_dependencies",
    description="Retrieves host dependencies for the given host",
    inputSchema={
        "type": "object",
        "properties": {
            "host_name": {
                "type": "string",
                "description": "Name of the host"
            },
            "master_name": {
                "type": "string",
                "description": "Name of the master host"
            },
            "dependent_host": {
                "type": "string",
                "description": "Name of the dependent host"
            }
        }
    }
)

get_service_dependencies = types.Tool(
    name="get_service_dependencies",
    description="Retrieves service dependencies for the given host",
    inputSchema={
        "type": "object",
        "properties": {
            "host_name": {
                "type": "string",
                "description": "Name of the host"
            },
            "service_description": {
                "type": "string",
                "description": "Description of the service of the host"
            },
            "master_host": {
                "type": "string",
                "description": "Name of the master host"
            },
            "master_service_description": {
                "type": "string",
                "description": "Description of the service of the master host"
            }
        }
    }
)

get_contacts_for_object = types.Tool(
    name="get_contacts_for_object",
    description="Retrieves the list of contacts to inform for an object",
    inputSchema={
        "type": "object",
        "properties": {
            "object_type": {
                "type": "string",
                "description": "The type of the object"
            },
            "object_name": {
                "type": "string",
                "description": "The object name"
            },
            "service_description": {
                "type": "string",
                "description": "Description of the service"
            }
        },
        "required": ["object_type", "object_name"]
    }
)

get_comments = types.Tool(
    name="get_comments",
    description="Retrieves comments based on the host and service",
    inputSchema={
        "type": "object",
        "properties": {
            "host_name": {
                "type": "string",
                "description": "The name of the host"
            },
            "service_description": {
                "type": "string",
                "description": "The description of the service"
            },
            "limit": {
                "type": "integer",
                "description": "The maximum number of comments to fetch",
                "default": 50
            }
        }
    }
)

get_comment_by_id = types.Tool(
    name="get_comment_by_id",
    description="Retrieves comments for the given comment id",
    inputSchema={
        "type": "object",
        "properties": {
            "comment_id": {
                "type": "string",
                "description": "The `comment_id` for the comment to fetch"
            }
        },
        "required": ["comment_id"]
    }
)

get_downtimes = types.Tool(
    name="get_downtimes",
    description="Retrieves the information for the downtimes in the Nagios Host Process",
    inputSchema={
        "type": "object",
        "properties": {
            "host_name": {
                "type": "string",
                "description": "The name of the host"
            },
            "service_description": {
                "type": "string",
                "description": "The description of the service"
            },
            "active_only": {
                "type": "boolean",
                "description": "Whether to fetch only the active downtimes"
            },
            "limit": {
                "type": "integer",
                "description": "The maximum number of the downtime logs to fetch",
                "default": 50
            }
        }
    }
)

def handle_tool_calls(tool_name: str, arguments: dict) -> List[types.TextContent]:
    """Handle tool execution requests"""
    try:
        logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")
        if tool_name == "get_host_status":
            host_name = arguments["host_name"] if "host_name" in arguments else None
            host_status_filter = arguments["host_status_filter"] if "host_status_filter" in arguments else None
            host_group_filter = arguments["host_group_filter"] if "host_group_filter" in arguments else None

            output = get_host_status_fn(host_name, host_status_filter, host_group_filter)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_service_status":
            host_name = arguments["host_name"] if "host_name" in arguments else None
            service_description = arguments["service_description"] if "service_description" in arguments else None
            service_status_filter = arguments["service_status_filter"] if "service_status_filter" in arguments else None

            output = get_service_status_fn(host_name, service_description, service_status_filter)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_alerts":
            output = get_alerts_fn()
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_nagios_process_info":
            output = get_nagios_process_info_fn()
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_hosts_in_group_status":
            if "host_group_name" not in arguments:
                raise ValueError("Missing `host_group_name` argument.")
            host_group_name = arguments["host_group_name"]
            host_status_filter = arguments["host_status_filter"] if "host_status_filter" in arguments else None

            output = get_hosts_in_group_status_fn(host_group_name, host_status_filter)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_services_in_group_status":
            if "service_group_name" not in arguments:
                raise ValueError("Missing `service_group_name` argument.")
            service_group_name = arguments["service_group_name"]
            service_status_filter = arguments["service_status_filter"] if "service_status_filter" in arguments else None

            output =  get_services_in_group_status_fn(service_group_name, service_status_filter)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_services_on_host_in_group_status":
            if "host_group_name" not in arguments:
                raise ValueError("Missing `host_group_name` argument.")
            if "host_name" not in arguments:
                raise ValueError("Missing `host_name` argument.")
            host_group_name = arguments["host_group_name"]
            host_name = arguments["host_name"]
            service_status_filter = arguments["service_status_filter"] if "service_status_filter" in arguments else None

            output = get_services_on_host_in_group_status_fn(host_group_name, host_name, service_status_filter)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_overall_health_summary":
            output = get_overall_health_summary_fn()
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_unhandled_problems":
            problem_type = arguments["problem_type"] if "problem_type" in arguments else None
            if problem_type is None:
                output = get_unhandled_problems_fn()
            else:
                output = get_unhandled_problems_fn(problem_type)

            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_object_list_config":
            if "object_type_plural" not in arguments:
                raise ValueError("Missing `object_type_plural` argument.")
            object_type_plural = arguments["object_type_plural"]

            output = get_object_list_config_fn(object_type_plural)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_single_object_config":
            if "object_type_singular" not in arguments:
                raise ValueError("Missing `object_type_singular` argument.")
            if "object_name" not in arguments:
                raise ValueError("Missing `object_name` arguement.")

            object_type_singular = arguments["object_type_singular"]
            object_name = arguments["object_name"]
            service_description_for_service = arguments["service_description_for_service"] if "service_description_for_service" in arguments else None

            output = get_single_object_config_fn(object_type_singular, object_name, service_description_for_service)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_host_dependencies":
            host_name = arguments["host_name"] if "host_name" in arguments else None
            master_host = arguments["master_host"] if "master_host" in arguments else None
            dependent_host = arguments["dependent_host"] if "dependent_host" in arguments else None

            output = get_host_dependencies_fn(host_name, master_host, dependent_host)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_service_dependencies":
            host_name = arguments["host_name"] if "host_name" in arguments else None
            service_description = arguments["service_description"] if "service_description" in arguments else None
            master_host = arguments["master_host"] if "master_host" in arguments else None
            master_service_description = arguments["master_service_description"] if "master_service_description" in arguments else None

            output = get_service_dependencies_fn(host_name, service_description, master_host, master_service_description)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_contacts_for_object":
            if "object_type" not in arguments:
                raise ValueError("Missing `object_type` argument.")
            if "object_name" not in arguments:
                raise ValueError("Missing `object_name` argument")

            object_type = arguments["object_type"]
            object_name = arguments["object_name"]
            service_description = arguments["service_description"] if "service_description" not in arguments else None

            output = get_contacts_for_object_fn(object_type, object_name, service_description)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_comments":
            host_name = arguments["host_name"] if "host_name" in arguments else None
            service_description = arguments["service_description"] if "service_description" in arguments else None
            limit = arguments["limit"] if "limit" in arguments else None

            if limit is None:
                output = get_comments_fn(host_name, service_description)
            else:
                output = get_comments_fn(host_name, service_description, limit)

            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_comment_by_id":
            if "comment_id" not in arguments:
                raise ValueError("Missing `comment_id` argument.")
            comment_id = arguments["comment_id"]

            output = get_comment_by_id_fn(comment_id)
            return [types.TextContent(type="text", text=str(output))]

        elif tool_name == "get_downtimes":
            host_name = arguments["host_name"] if "host_name" in arguments else None
            service_description = arguments["service_description"] if "service_description" in arguments else None
            active_only = arguments["active_only"] if "active_only" in arguments else None
            limit = arguments["limit"] if "limit" in arguments else None

            if limit:
                output = get_downtimes_fn(host_name, service_description, active_only, limit)
            else:
                output = get_downtimes_fn(host_name, service_description, active_only)

            return [types.TextContent(type="text", text=str(output))]

        else:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=f"Error: {error_msg}")]

    except ValueError as e:
        error_msg = f"Invalid arguments for {tool_name}: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=f"Error: {error_msg}")]

    except ConnectionError as e:
        error_msg = f"Failed to connect to Nagios: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=f"Error: {error_msg}")]

    except Exception as e:
        error_msg = f"Unexpected error in {tool_name}: {str(e)}"
        logger.exception(error_msg)
        return [types.TextContent(type="text", text=f"Error: {error_msg}")]
