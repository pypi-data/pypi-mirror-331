import asyncio
from logging import getLogger
from .types.setting import BigGoMCPSetting
from .lib.server_setup import create_server

logger = getLogger(__name__)


async def start():
    setting = BigGoMCPSetting()
    server = await create_server(setting)

    logger.info("Starting BigGo MCP Server. type: %s", setting.server_type)

    if setting.server_type == "sse":
        await server.run_sse_async()
    else:
        await server.run_stdio_async()


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
