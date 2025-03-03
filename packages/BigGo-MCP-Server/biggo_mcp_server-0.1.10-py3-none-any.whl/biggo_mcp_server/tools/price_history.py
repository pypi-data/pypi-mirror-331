from logging import getLogger
from typing import Annotated
from mcp.server.fastmcp import Context
from pydantic import Field
from ..types.responses import PriceHisotryGraphToolResponse, PriceHistoryToolResponse
from ..services.price_history import DAYS, PriceHistoryService
from ..lib.utils import get_setting

logger = getLogger(__name__)


def price_history_graph(
    ctx: Context,
    history_id: Annotated[
        str,
        Field(description="""
              Product History ID
              Here are a few steps to obtain this argument.
              1. Use 'product_search' tool to retrive a list of products
              2. Find the most relevant product.
              3. The product should have a field called 'history_id', use it as the value for this argument
              """,
              examples=[
                  "tw_pmall_rakuten-nwdsl_6MONJRBOO", "tw_pec_senao-1363332"
              ])],
) -> str:
    """Link That Visualizes Product Price History"""

    logger.info("price history graph, history_id: %s", history_id)

    setting = get_setting(ctx)
    service = PriceHistoryService(setting)
    url = service.graph_link(history_id)

    return PriceHisotryGraphToolResponse(
        price_history_graph=f"![Price History Graph]({url})").slim_dump()


async def price_history_with_history_id(
    ctx: Context,
    history_id: Annotated[
        str,
        Field(description="""
              Product History ID
              Here are a few steps to obtain this argument.
              1. Use 'product_search' tool to retrive a list of products
              2. Find the most relevant product.
              3. The product should have a field called 'history_id', use it as the value for this argument
              """,
              examples=[
                  "tw_pmall_rakuten-nwdsl_6MONJRBOO", "tw_pec_senao-1363332"
              ])],
    days: Annotated[DAYS, Field(description="History range")],
) -> str:
    """Product Price History With History ID"""

    logger.info("price history with history id, history_id: %s, days: %s",
                history_id, days)

    setting = get_setting(ctx)
    service = PriceHistoryService(setting)
    ret = await service.history_with_history_id(history_id=history_id,
                                                days=days)
    if ret is None:
        return "No price history found"

    return PriceHistoryToolResponse(
        price_history_description=ret.description,
        price_history_graph=f"![Price History Graph]({ret.graph_link})"
    ).slim_dump()


async def price_history_with_url(
    ctx: Context,
    days: Annotated[DAYS, Field(description="History range")],
    url: Annotated[str, Field(description="Product URL")],
) -> str:
    """Product Price History With URL"""

    logger.info("price history with url, url: %s, days: %s", url, days)

    setting = get_setting(ctx)
    service = PriceHistoryService(setting)
    ret = await service.history_with_url(url=url, days=days)
    if ret is None:
        return "No price history found"

    return PriceHistoryToolResponse(
        price_history_description=ret.description,
        price_history_graph=f"![Price History Graph]({ret.graph_link})"
    ).slim_dump()
