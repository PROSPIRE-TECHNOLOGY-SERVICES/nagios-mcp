"""
Entry point for running nagios_mcp module
"""

import asyncio

from .server import main

if __name__=="__main__":
    import asyncio
    import logging
    import sys

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        sys.exit(0)
