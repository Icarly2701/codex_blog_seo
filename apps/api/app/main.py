from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.auth import get_bearer_token
from app.config import settings
from app.schemas import GenerateRequest, GenerateResponse, HealthResponse, PostsResponse
from app.services.openai_client import generate_markdown
from app.services.supabase_client import SupabaseRepository, current_month_key
from app.services.usage import UsageState, can_generate, increment_count, remaining_quota

app = FastAPI(title="Blog SEO Writer API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_repo() -> SupabaseRepository:
    return SupabaseRepository()


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/v1/posts", response_model=PostsResponse)
def list_posts(
    token: str = Depends(get_bearer_token),
    repo: SupabaseRepository = Depends(get_repo),
) -> PostsResponse:
    user_id = repo.get_user_id_from_token(token)
    items = repo.list_posts(user_id)
    return PostsResponse(items=items)


@app.post("/v1/generate", response_model=GenerateResponse)
def generate_post(
    body: GenerateRequest,
    token: str = Depends(get_bearer_token),
    repo: SupabaseRepository = Depends(get_repo),
) -> GenerateResponse:
    user_id = repo.get_user_id_from_token(token)
    month = current_month_key()

    usage = repo.get_usage(user_id=user_id, month=month)
    if usage is None:
        usage = repo.upsert_default_usage(user_id=user_id, month=month)

    state = UsageState(count=int(usage["count"]), limit=int(usage["limit"]))
    if not can_generate(state):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly quota exceeded ({state.limit}/month)",
        )

    content = generate_markdown(keyword=body.keyword, tone=body.tone, length=body.length)

    next_state = increment_count(state)
    repo.update_usage_count(user_id=user_id, month=month, count=next_state.count)
    repo.insert_post(
        user_id=user_id,
        keyword=body.keyword,
        tone=body.tone,
        length=body.length,
        content=content,
    )

    return GenerateResponse(
        content=content,
        usage_count=next_state.count,
        usage_limit=next_state.limit,
        remaining=remaining_quota(next_state),
    )
