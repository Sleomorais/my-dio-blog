from pydantic import BaseModel, AwareDatetime, NaiveDatetime


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    published_at: AwareDatetime | NaiveDatetime | None