from pydantic import BaseModel


class CanopenItem(BaseModel):
    is_writeable: bool
    index: int


class CanopenVariable(CanopenItem):
    value: int | str | float | bool


class CanopenArray(CanopenItem):
    value: list[int | str | float]


class CanopenInvalid(CanopenItem):
    pass
