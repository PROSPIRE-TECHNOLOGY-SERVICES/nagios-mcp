import logging
import mcp.types as types
from typing import List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
import argparse
from dotenv import load_dotenv

from tools import *

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nagios-mcp-server")

# Create the server instance
server = Server("nagios-mcp-server")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available Nagios MCP Tools"""
    logging.info("Listing available tools")
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
    """Handle tool calls"""
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    return handle_tool_calls(name, arguments)

async def run_stdio():
    """Run server with stdio transport"""
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

async def run_sse(host: str="localhost", port: int=8000):
    """Run server with sse transport"""

    # Create SSE Server app
    sse_transport = SseServerTransport("/messages")

    async def handle_sse(request):
        """Handle SSE connections"""
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            read_stream, write_stream = streams
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
        # returning empty response to avoid NoneType error
        return Response()

    # Create Starlette routes
    routes = [
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages", app=sse_transport.handle_post_message)
    ]

    # Create Starlette app
    app = Starlette(routes=routes)

    logging.info(f"Server running with SSE transport on http://{host}:{port}")
    logging.info(f"SSE endpoint: http://{host}:{port}/sse")

    # Configure and run uvicorn
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info"
    )

    server_instance = uvicorn.Server(config)
    await server_instance.serve()

async def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(description="Nagios MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport method to use (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to for SSE transport (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for SSE transport (default: 8000)"
    )

    args = parser.parse_args()

    if args.transport == "sse":
        await run_sse(args.host, args.port)
    else:
        await run_stdio()

if __name__=="__main__":
    import asyncio
    import sys

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        sys.exit(0)
