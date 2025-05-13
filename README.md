# nagios-mcp
MCP Server for Nagios Core.

This server is built by us for the Nagios Core web-client.
The code for the server can be found [here](https://github.com/PROSPIRE-TECHNOLOGY-SERVICES/AIOps-Agent/tree/main/aiops_agent/nagios_mcp.py).
The server utilizes the CGI binaries located at the `cgi-bin` or `sbin` folder in your Nagios folder.
More specifically the `statusjson.cgi` and `objectjson.cgi` files for the purpose of the status and configuration tooling.

## How to install:
### For Claude Desktop

```
# If uv is not installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repo
git clone https://github.com/PROSPIRE-TECHNOLOGY-SERVICES/nagios-mcp.git

# Run the following line to install directly to Claude Desktop
uv run mcp install server.py
```

Create `.env` file with the Nagios Core variables and keep it in the repo
```
NAGIOS_URL="http://localhost/nagios"
NAGIOS_USER="your_nagios_core_username"
NAGIOS_PASS="your_nagios_core_password"
```

### For Cursor
- To setup the server in Cursor, go to `Setting` -> `MCP` -> `Add new global MCP server`, and add the following:
```
{
  "mcpServers": {
    "nagios": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE_PATH_TO/nagios-mcp", # Make sure this directory is correct
        "run",
        "server.py"
      ]
    }
  }
}
```

### For 5ire
5ire is another MCP client. For setting up in 5ire, go to `Tools` -> `New` and add the following configuration.
1. Tool Key: `Nagios`
2. Name: `NagiosMCP`
3. Command: `uv --directory /ABSOLUTE_PATH_TO/nagios-mcp run server.py`

### List of Tools:
| Tool Name                              | Tool Description                                                                     |
| -------------------------------------- | ------------------------------------------------------------------------------------ |
| `get_host_status`                      | Retrieves status for all hosts or a specific host.                                   |
| `get_service_status`                   | Retrieves status for services using `statusjson.cgi`.                                  |
| `get_alerts`                           | Retrieves current problematic host and service states (alerts).                      |
| `get_program_status`                   | Retrieves the Nagios Core program status from statusjson.cgi                           |
| `get_hosts_in_group_status`            | Retrieves status for all hosts within a specific host group.                         |
| `get_services_in_group_status`         | Retrieves status for all services within a specific service group.                   |
| `get_services_on_host_in_group_status` | Retrieves status for all the services with a specific host group.                     |
| `get_overall_health_summary`           | Retrieves overall health summary for all the hosts and services.                     |
| `get_unhandled_problems`               | Retrieves all the unhandled problems for all the hosts and services.                 |
| `get_object_list_config`               | Retrieves configuration list for object types like "hosts", "services", "hostgroups", etc. |
| `get_single_object_config`             | Retrieves configuration for a single specific object.                                |
| `get_host_dependencies`                | Retrieves host dependencies for the given host.                                      |
| `get_service_dependencies`             | Retrieves service dependencies for the given host.                                   |
| `get_contacts_for_object`              | Retrieves the list of contacts to inform for an object.                              |
| `get_comments`                         | Retrieves comments based on the host and service.                                    |
| `get_comment_by_id`                    | Retrieves comments for the given comment id.                                         |
| `get_downtimes`                        | Retrieves the information for the downtimes in the Nagios Host Process.              |
| `get_nagios_process_info`              | Returns the information for the Nagios process. (Alias for get_program_status function) |

- Currently all the tools use GET requests. Other useful tools and tools requiring POST requests will be added soon.

## How the MCP server works?
- Nagios Core web-client is typically hosted on `http://YOUR_HOST/nagios/`
- The MCP server reads the details about the processes and services using the CGI binaries, they can be found in the `cgi-bin` or `sbin` sub-directory in your Nagios main directory.
- The Status Tools and Config Tools use the `cgi-bin/statusjson.cgi` and `cgi-bin/objectjson.cgi` files respectively for retrieving the information.
