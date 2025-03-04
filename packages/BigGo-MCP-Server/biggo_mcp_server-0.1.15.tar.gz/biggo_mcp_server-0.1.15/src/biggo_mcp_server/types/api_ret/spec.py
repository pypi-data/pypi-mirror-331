from pydantic import BaseModel, Field, RootModel


class SpecIndexesAPIItem(BaseModel):
    index: str


class SpecIndexesAPIRet(RootModel):
    root: list[SpecIndexesAPIItem] = Field(default_factory=list)


class SpecMappingAPIRet(RootModel):
    """
    Example:
    {
        "spec_grouping_bidet_toilet_seat": {
            "mappings": {
                "properties": {}
            }
        }
    }
    """
    root: dict[str, dict] = Field(default_factory=dict)


class SpecSearchAPIRet(RootModel):
    root: list[dict]
