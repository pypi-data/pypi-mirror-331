from pydantic import BaseModel, HttpUrl


class Resp(BaseModel):
    payMethodId: int
    name: str
    defaultName: str | None = None
    template: int
    bankImage: HttpUrl
    bankImageWeb: HttpUrl
    bankType: int
    color: str
