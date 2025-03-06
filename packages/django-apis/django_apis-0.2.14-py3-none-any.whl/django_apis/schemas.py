from typing import Any
from typing import List
from typing import Type
from typing import Callable
from typing import Union
from typing import Dict

from pydantic import VERSION as PYDANTIC_VERSION
from pydantic import Field
from pydantic import BaseModel
from pydantic_core.core_schema import CoreSchema
from pydantic_core.core_schema import with_info_plain_validator_function
from pydantic.json_schema import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue

from django.core.files.uploadedfile import UploadedFile as DjangoUploadedFile

__all__ = [
    "ResponseBase",
    "SimpleResponse",
    "UploadedFile",
    "OptionalUploadedFile",
    "OptionalUploadedFiles",
    "RequiredUploadedFile",
    "RequiredUploadedFiles",
]

PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")


class ResponseBase(BaseModel):
    pass


class SimpleResponse(ResponseBase):
    code: int = Field(
        default=0,
        description="错误码。正确时为：0。",
    )
    message: str = Field(
        default="OK",
        description="错误消息。正确时为：OK。",
    )
    data: Any = Field(
        default=None,
        description="业务数据。不同接口有不同类型的业务数据。",
    )


class UploadedFile(DjangoUploadedFile):

    @classmethod
    def _validate(
        cls,
        __input_value: Any,
        _: Any,
    ) -> "UploadedFile":
        if not isinstance(__input_value, DjangoUploadedFile):
            raise ValueError(f"Expected UploadFile, received: {type(__input_value)}")
        return __input_value

    if not PYDANTIC_V2:

        @classmethod
        def __modify_schema__(
            cls,
            field_schema: Dict[str, Any],
        ) -> None:
            field_schema.update({"type": "string", "format": "binary"})

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return {"type": "string", "format": "binary"}

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source: Type[Any],
        handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return with_info_plain_validator_function(cls._validate)


OptionalUploadedFile = Union[UploadedFile, None]
OptionalUploadedFiles = Union[List[UploadedFile], UploadedFile, None]

RequiredUploadedFile = UploadedFile
RequiredUploadedFiles = Union[List[UploadedFile], UploadedFile]
