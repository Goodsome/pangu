import logging
import os
from pathlib import Path

from fastmcp import FastMCP
from foundation.logging_setup import configure_logging
from spike.interfaces.mcp.router import SPIKE_TOOLS

from pangu_mcp.bootstrap.container import create_container

logger = logging.getLogger(__name__)


def create_app():
    mcp = FastMCP("Pangu")

    for tool in SPIKE_TOOLS:
        _ = mcp.add_tool(tool)
    return mcp


def main():

    log_dir = Path.home() / ".pangu" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    configure_logging(
        app_name="mcp",
        log_dir=log_dir,
        console_output=False,
    )
    container = None
    try:
        container = create_container(init_resources=False)
        container.wire(packages=["spike.interfaces.mcp"])
        mcp = create_app()
        logger.info("Starting MCP server")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("接收到退出信号，正在安全关闭...")
    except Exception as e:
        logger.error(f"MCP server failed to start: {str(e)}", exc_info=True)
    finally:
        if container:
            container.shutdown_resources()
        logger.info("MCP server stopped")
        os._exit(0)


if __name__ == "__main__":
    main()
