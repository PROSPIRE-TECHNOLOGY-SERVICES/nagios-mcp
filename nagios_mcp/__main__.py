"""
Entry point for running nagios_mcp module
"""

import asyncio

from .server import main as server_main


def main():
    import logging
    import sys

    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        sys.exit(0)

if __name__=="__main__":
    main()
