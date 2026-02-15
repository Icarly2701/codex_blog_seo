from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    keyword: str = Field(min_length=1)
    tone: str = "전문적이지만 이해하기 쉽게"
    length: int = Field(default=2000, ge=500, le=5000)


class GenerateResponse(BaseModel):
    content: str
    usage_count: int
    usage_limit: int
    remaining: int


class PostItem(BaseModel):
    id: str
    keyword: str
    tone: str | None = None
    length: int | None = None
    content: str
    created_at: str


class PostsResponse(BaseModel):
    items: list[PostItem]


class HealthResponse(BaseModel):
    status: str
