# from typing import Literal, TypedDict, Annotated
from typing_extensions import Literal,Annotated, TypedDict

class Column(TypedDict):
    id: str
    name: str
    type: str
    datasetID: str
    description: str
    displayName: str
    ordinalPosition: int
    sortingSettingID: str
    visible: bool


class Dataset(TypedDict):
    id: str
    name: str
    description: str
    sourceType: str
    siteName: str
    sourceURL: str
    columns: list[Column]


admin_level = {
  "Taiwan": {
    "zh-tw": {
      "admin_level_2": "國家",
      "admin_level_4": "直轄市/縣市",
      "admin_level_7": "直轄市的區",
      "admin_level_8": "縣轄市/鄉鎮",
      "admin_level_9": "村/里",
      "admin_level_10": "鄰"
    },
    "zh-cn": {
      "admin_level_2": "国家",
      "admin_level_4": "直辖市/县市",
      "admin_level_7": "直辖市的区",
      "admin_level_8": "县辖市/乡镇",
      "admin_level_9": "村/里",
      "admin_level_10": "邻"
    },
    "en": {
      "admin_level_2": "Country",
      "admin_level_4": "Municipality/County",
      "admin_level_7": "District",
      "admin_level_8": "County-Administered City/Township",
      "admin_level_9": "Village",
      "admin_level_10": "Neighbourhood"
    }
  }
}

class XAxis(TypedDict):
    columnID: Annotated[str, "Column ID for the x-axis. Refer to dataset.columns[].id. Column需要來自使用的dataset."]
    column_name: Annotated[str, "Column name for the x-axis. Refer to dataset.columns[].name. 需要和columnID對應"]
    type: Annotated[str, "Type of data. Refer to dataset.columns[].type.  需要和columnID對應"]
    country: Annotated[Literal["Taiwan"], "Where dataset is from."]
    language: Annotated[Literal["zh-tw", "zh-cn", "en"], "Language of the dataset."]
    format: Annotated[str, f'''
        1.If column type is date/datetime, format should be one of ["year","quarter","month","week","date","day","weekday","year_month","year_quarter","year_week","month_day","day_hour","hour","minute","second","hour_minute","time"]。
        2.If column type is space, the format should be {admin_level} base on country and language (e.g. admin_level_2,admin_level_4)
    ''']

class YAxis(TypedDict):
    columnID: Annotated[str, "Column ID for the y-axis. Refer to dataset.columns[].id. Column需要來自使用的dataset."]
    column_name: Annotated[str, "Column name for the y-axis. Refer to dataset.columns[].name.  需要和columnID對應"]
    type: Annotated[str, "Type of data. Refer to dataset.columns[].type.  需要和columnID對應"]
    calculation: Annotated[
        Literal["count", "sum", "avg", "min", "max", "distinct_count"],
        "Aggregate function used on y-axis. Valid options depend on column type. If column type is \"nominal\" or \"ordinal\", calculation should be one of [\"count\",\"distinct_count\"]. If column type is \"date\" or \"datetime\", calculation should be one of [\"count\",\"min\",\"max\",\"distinct_count\"]."
    ]

class Query(TypedDict):
    sourceURL: Annotated[str, "API endpoint of the dataset.Refer to dataset.sourceURL."]
    dataset_id: Annotated[str, "Unique ID of the dataset.Refer to dataset.id."]
    dataset_name: Annotated[str, "Human-readable name of the dataset.Refer to dataset.name."]
    x: Annotated[list[XAxis], "You may use up to three x-axes on the graph."]
    y: Annotated[list[YAxis], "You may use up to two y-axes on the graph."]


class QueryResult(TypedDict):
    dataset_name: str
    x: str
    y: str
    charts_data: list[dict[str, str]]   # todo: Double check this type