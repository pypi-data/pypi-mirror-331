from typing import TypedDict, Literal, NotRequired, Protocol, Optional, Any
from pandas import DataFrame


class ScikitModel(Protocol):
    def predict_proba(self, X) -> Optional[Any]: ...


class ViewMeta(TypedDict):
    mode: NotRequired[Literal["public", "protected", "private"]]
    view_id: NotRequired[str]
    dataset_name: NotRequired[str]


class ValuateModelOutput(TypedDict):
    view_id: str
    view_url: str


class Credentials(TypedDict):
    email: str
    password: str


class AWSVariables(TypedDict):
    api_url: NotRequired[str]
    app_client_id: NotRequired[str]
    identity_pool_id: NotRequired[str]
    user_pool_id: NotRequired[str]
    bucket_name: NotRequired[str]
    base_url: NotRequired[str]
    validation_api_url: NotRequired[str]


class ColumnNames(TypedDict):
    dataset_column_names: NotRequired[list[str]]
    score_column_names: NotRequired[list[str]]
    dependent_variable_name: NotRequired[str]
