from typing import Union
from pydantic import BaseModel, Field


class ApiBaseModel(BaseModel):
    pass


class ApiBaseModel(ApiBaseModel):
    id: str = Field(min_length=1)


class ApiBaseModelAndDesc(ApiBaseModel):
    description: Union[str, None] = None


class ApiBaseModelName(ApiBaseModel):
    name: str = Field(min_length=1)


class ApiBaseModelNameLabelDesc(ApiBaseModelName):
    label: Union[str, None] = None
    description: Union[str, None] = None


class ApiBaseModelNameLabel(ApiBaseModelName):
    label: Union[str, None] = None


class ApiBaseModelNameDesc(ApiBaseModelName):
    description: Union[str, None] = None
