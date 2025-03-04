import asyncio
from logging import getLogger
from .types.setting import BigGoMCPSetting
from .lib.server_setup import create_server

logger = getLogger(__name__)


async def start():
    logger.info("Starting BigGo MCP Server")

    setting = BigGoMCPSetting()
    server = await create_server(setting)
    server_bg: list[asyncio.Task] = []

    logger.info("Starting STDIO BigGo MCP Server")
    server_bg.append(
        asyncio.create_task(server.run_stdio_async(), name="stdio-async"))

    if setting.server_type == "sse":
        logger.info("Starting SSE BigGo MCP Server")
        server_bg.append(
            asyncio.create_task(server.run_sse_async(), name="sse-async"))

    await asyncio.gather(*server_bg)


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
