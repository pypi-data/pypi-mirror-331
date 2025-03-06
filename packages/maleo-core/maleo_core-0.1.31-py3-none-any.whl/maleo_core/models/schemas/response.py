from typing import Literal, Optional, Any
from pydantic import BaseModel
from ..transfers.payload import Pagination

class Response:
    #* ----- ----- ----- Base ----- ----- ----- *#
    class Base(BaseModel):
        success:Literal[True, False]
        code:str
        message:str
        description:str

    #* ----- ----- ----- Derived ----- ----- ----- *#
    class Fail(Base):
        success:Literal[False] = False
        other:Optional[Any] = None

    class Unauthorized(Fail):
        code:str = "MAL-ATH-001"
        message:str = "Unauthorized Request"

    class Forbidden(Fail):
        code:str = "MAL-ATH-002"
        message:str = "Forbidden Request"

    class SingleData(Base):
        success:Literal[True] = True
        data:Any
        other:Optional[Any] = None

    class MultipleData(Base):
        success:Literal[True] = True
        data:list[Any]
        pagination:Pagination
        other:Optional[Any] = None