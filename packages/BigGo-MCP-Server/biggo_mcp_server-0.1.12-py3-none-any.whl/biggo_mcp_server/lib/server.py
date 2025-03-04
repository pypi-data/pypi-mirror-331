from logging import getLogger
from mcp.server.fastmcp import FastMCP
from ..types.setting import BigGoMCPSetting

logger = getLogger(__name__)


class BigGoMCPServer(FastMCP):

    def __init__(self, setting: BigGoMCPSetting):
        super().__init__("BigGo MCP Server")
        self._biggo_setting = setting
        self.settings.port = setting.sse_port

    @property
    def biggo_setting(self) -> BigGoMCPSetting:
        return self._biggo_setting
