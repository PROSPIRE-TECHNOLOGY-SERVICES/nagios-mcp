import logging
import mcp.types as types
from typing import Dict, Any, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.server.stdio import stdio_server

from tools import *

logger = logging.getLogger("nagios-mcp-server")
logger.info("Starting Nagios MCP Server")

server = Server("nagios-mcp-server")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available Nagios MCP Tools"""
    return [
        get_host_status,
        get_service_status,
        get_alerts,
        get_nagios_process_info,
        get_hosts_in_group_status,
        get_services_in_group_status,
        get_services_on_host_in_group_status,
        get_overall_health_summary,
        get_unhandled_problems,
        get_object_list_config,
        get_single_object_config,
        get_host_dependencies,
        get_service_dependencies,
        get_contacts_for_object,
        get_comments,
        get_comment_by_id,
        get_downtimes
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    return handle_tool_calls(name, arguments)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        logging.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nagios",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__=="__main__":
    import asyncio
    asyncio.run(main())
