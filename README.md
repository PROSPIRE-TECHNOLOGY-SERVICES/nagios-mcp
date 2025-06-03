# nagios-mcp

MCP Server for Nagios Core.

This server is built by us for the Nagios Core web-client.
The code for the server can be found [here](https://github.com/PROSPIRE-TECHNOLOGY-SERVICES/AIOps-Agent/tree/main/aiops_agent/nagios_mcp.py).
The server utilizes the CGI binaries located at the `cgi-bin` or `sbin` folder in your Nagios folder.
More specifically the `statusjson.cgi` and `objectjson.cgi` files for the purpose of the status and configuration tooling.

## How to install:

### Setting up

- Installing `uv`
    - Linux or MacOS or WSL:
      ```bash
      curl -LsSf https://astral.sh/uv/install.sh | sh
      ```
    - Windows:
      ```
      powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
      ```

Or installing using `pip`:
```bash
pip install uv
```

- Cloning the repository
```
git clone https://github.com/PROSPIRE-TECHNOLOGY-SERVICES/nagios-mcp.git
```

- Creating a config file
Create a `nagios_config.yaml` or `nagios_config.json` file with the configuration parameters given below.

```yaml
nagios_url: "http://localhost/nagios"
nagios_user: "your_nagios_core_username"
nagios_pass: "your_nagios_core_password"
```

### Starting the SSE server

- The mcp server by default runs on STDIO transport. If you do not require SSE transport, you can skip this section.
- Command: `uv run -m nagios_mcp --config NAGIOS_CONFIG_FILE --transport sse --host localhost --port 8000`

### For Claude Desktop

- [Official setup guide](https://modelcontextprotocol.io/quickstart/user#mac-os-linux)
- For setting up in [Claude Desktop](https://claude.ai/download), go to `Settings` -> `Developer` -> `Edit Config`. Or directly modify the config file,
    - MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
    - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Add the following block to the config file,
```json
{
    "mcpServers": {
        "nagios": {
            "command": "uv",
            "args": [
                "--directory", "/ABSOLUTE_PATH_TO/nagios-mcp",
                "run",
                "-m",
                "nagios_mcp",
                "--config", "PATH_TO_THE_NAGIOS_CONFIG_FILE"
            ]
        }
    }
}
```
- For SSE transport:
```json
{
    "mcpServers": {
        "nagios": {
            "url": "http://localhost:8000/sse" # change this if you are using different port
        }
    }
}
```

### For Cursor

- [Official setup guide](https://docs.cursor.com/context/model-context-protocol)
- To setup the server in [Cursor](https://www.cursor.com/), go to `Setting` -> `MCP` -> `Add new global MCP server`, and add the following:
  For STDIO transport:
```json
{
  "mcpServers": {
    "nagios": {
        "command": "uv",
        "args": [
                "--directory",
                "/ABSOLUTE_PATH_TO/nagios-mcp", # Make sure this directory is correct
                "run",
                "-m",
                "nagios_mcp",
                "--config", "PATH_TO_THE_NAGIOS_CONFIG_FILE"
            ],
        }
    }
}
```
- For SSE Transport:
```json
{
    "mcpServers": {
        "nagios": {
            "url": "http://localhost:8000/sse" # change this if you are using different port
        }
    }
}
```

### For Windsurf

- [Official setup guide](https://docs.windsurf.com/windsurf/cascade/mcp)
- For setting up the server in [Windsurf](https://windsurf.com/), add the following lines to the `~/.codeium/windsurf/mcp_config.json` file.
```json
{
    "mcpServers": {
        "nagios": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE_PATH_TO/nagios-mcp", # Make sure this directory is correct
                "run",
                "-m",
                "nagios_mcp",
                "--config", "PATH_TO_THE_NAGIOS_CONFIG_FILE"
            ],
        }
    }
}
```
- For SSE Transport:
```json
{
    "mcpServers": {
        "nagios": {
            "serverUrl": "http://localhost:8000/sse" # change this if you are using different port
        }
    }
}
```

### For Cline

- [Official setup guide](https://docs.cline.bot/mcp/configuring-mcp-servers)
- For setting up the server in [Cline](https://cline.bot/), go to `MCP Servers` -> `Installed` -> `Configure MCP Servers`, this will open the `cline_mcp_settings.json` file. Add the following code block to the file.
```json
{
    "mcpServers": {
        "nagios": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE_PATH_TO/nagios-mcp", # Make sure this directory is correct
                "run",
                "-m",
                "nagios_mcp",
                "--config", "PATH_TO_THE_NAGIOS_CONFIG_FILE"
            ],
        }
    }
}
```
- For SSE Transport:
```json
{
    "mcpServers": {
        "nagios": {
            "url": "http://localhost:8000/sse" # change this if you are using different port
        }
    }
}
```

### For 5ire

5ire is another MCP client. For setting up in 5ire, go to `Tools` -> `New` and add the following configuration.

1. Tool Key: `Nagios`
2. Name: `NagiosMCP`
3. Command: `uv --directory /ABSOLUTE_PATH_TO/nagios-mcp run -m nagios_mcp --config PATH_TO_THE_NAGIOS_CONFIG_FILE`

### List of Tools:

| Tool Name                              | Tool Description                                                                           |
| -------------------------------------- | ------------------------------------------------------------------------------------------ |
| `get_host_status`                      | Retrieves status for all hosts or a specific host.                                         |
| `get_service_status`                   | Retrieves status for services using `statusjson.cgi`.                                      |
| `get_alerts`                           | Retrieves current problematic host and service states (alerts).                            |
| `get_program_status`                   | Retrieves the Nagios Core program status from statusjson.cgi                               |
| `get_hosts_in_group_status`            | Retrieves status for all hosts within a specific host group.                               |
| `get_services_in_group_status`         | Retrieves status for all services within a specific service group.                         |
| `get_services_on_host_in_group_status` | Retrieves status for all the services with a specific host group.                          |
| `get_overall_health_summary`           | Retrieves overall health summary for all the hosts and services.                           |
| `get_unhandled_problems`               | Retrieves all the unhandled problems for all the hosts and services.                       |
| `get_object_list_config`               | Retrieves configuration list for object types like "hosts", "services", "hostgroups", etc. |
| `get_single_object_config`             | Retrieves configuration for a single specific object.                                      |
| `get_host_dependencies`                | Retrieves host dependencies for the given host.                                            |
| `get_service_dependencies`             | Retrieves service dependencies for the given host.                                         |
| `get_contacts_for_object`              | Retrieves the list of contacts to inform for an object.                                    |
| `get_comments`                         | Retrieves comments based on the host and service.                                          |
| `get_comment_by_id`                    | Retrieves comments for the given comment id.                                               |
| `get_downtimes`                        | Retrieves the information for the downtimes in the Nagios Host Process.                    |
| `get_nagios_process_info`              | Returns the information for the Nagios process. (Alias for get_program_status function)    |

- Currently all the tools use GET requests. Other useful tools and tools requiring POST requests will be added soon.

## How the MCP server works?

- Nagios Core web-client is typically hosted on `http://YOUR_HOST/nagios/`
- The MCP server reads the details about the processes and services using the CGI binaries, they can be found in the `cgi-bin` or `sbin` sub-directory in your Nagios main directory.
- The Status Tools and Config Tools use the `cgi-bin/statusjson.cgi` and `cgi-bin/objectjson.cgi` files respectively for retrieving the information.
