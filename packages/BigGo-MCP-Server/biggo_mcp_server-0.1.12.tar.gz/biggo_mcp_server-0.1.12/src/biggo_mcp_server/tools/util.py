from typing import Annotated
from mcp.server.fastmcp import Context
from pydantic import Field
from biggo_mcp_server.types.setting import Regions
from ..lib.utils import get_setting


def get_current_region(
    ctx: Context,
) -> Annotated[Regions, Field(description="Current region")]:
    """
    Get the current region setting.
    """
    setting = get_setting(ctx)
    return setting.region
