from logging import getLogger
from typing_extensions import Self
from pydantic import BaseModel, model_validator
from .api_ret.price_history import PriceHistoryAPIRet
from .api_ret.product_search import ProductSearchAPIRet

logger = getLogger(__name__)


class BaseToolResponse(BaseModel):

    def slim_dump(self) -> str:
        return self.model_dump_json(exclude_none=True)


class ProductSearchToolResponse(BaseToolResponse):
    product_search_result: ProductSearchAPIRet
    reason: str | None = None

    @model_validator(mode='after')
    def post_init(self) -> Self:
        if len(self.product_search_result.list) == 0:
            self.reason = """
No results found. Possible reasons:
1. This search is much more complex than a simple product search.
2. The user is asking things related to product specifications.

If the problems might be related to the points listed above,
please use the 'spec_search' tool and try again.
            """
        return self


class PriceHisotryGraphToolResponse(BaseToolResponse):
    price_history_graph: str


class PriceHistoryToolResponse(BaseToolResponse):
    price_history_description: PriceHistoryAPIRet
    price_history_graph: str


class SpecIndexesToolResponse(BaseToolResponse):
    indexes: list[str]


class SpecMappingToolResponse(BaseToolResponse):
    mappings: dict
    example_document: dict
    note: str = """
Specifications are under the 'specs' field
Example fields paths:
- specs.physical_specs.weight
- specs.technical_specs.water_resistance.depth
- specs.sensors.gyroscope
"""


class SpecSearchToolResponse(BaseToolResponse):
    hits: list[dict]
    reason: str | None = None

    @model_validator(mode='after')
    def post_init(self) -> Self:
        # remove documents with status == deleted
        cleaned_hits: list[dict] = []
        for hit in self.hits:
            if hit["_source"].get("status", None) == "deleted":
                continue
            else:
                cleaned_hits.append(hit)

        logger.debug("original hits: %s, cleaned_hits: %s", len(self.hits),
                     len(cleaned_hits))

        self.hits = cleaned_hits

        if len(self.hits) == 0:
            self.reason = """
No results found. Possible reasons:
1. You have no clue about the mapping.
2. You have not used the 'spec_mapping' tool to get the mapping of the index.
3. You have not filter out status == 'deleted' products in your query

Do you really know what you are doing?
You MUST think about this before you tell the user that no results are found.
You MUST be ABSOLUTELY sure that you understand the mapping of the index, and that the
search criteria is correct, and that there is TRULY no result.

If you have any doubt, please use the 'spec_mapping' tool to get the mapping of the index,
and try again.
The 'spec_mapping' tool will give you the mapping of the index, and an example document.
'spec_mapping' is the only way to understand the mapping of the index.
It is the best tool to use before you search the index.
            """

        return self
