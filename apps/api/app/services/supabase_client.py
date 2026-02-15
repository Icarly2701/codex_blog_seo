from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from supabase import Client, create_client

from app.config import settings


class SupabaseRepository:
    def __init__(self) -> None:
        self.client: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    def get_user_id_from_token(self, token: str) -> str:
        response = self.client.auth.get_user(token)
        user = response.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user.id

    def list_posts(self, user_id: str) -> list[dict[str, Any]]:
        response = (
            self.client.table("posts")
            .select("id,keyword,tone,length,content,created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []

    def get_usage(self, user_id: str, month: str) -> dict[str, Any] | None:
        response = (
            self.client.table("usage_monthly")
            .select("user_id,month,count,limit")
            .eq("user_id", user_id)
            .eq("month", month)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    def upsert_default_usage(self, user_id: str, month: str) -> dict[str, Any]:
        payload = {
            "user_id": user_id,
            "month": month,
            "count": 0,
            "limit": 3,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        response = self.client.table("usage_monthly").upsert(payload, on_conflict="user_id,month").execute()
        rows = response.data or []
        return rows[0] if rows else payload

    def update_usage_count(self, user_id: str, month: str, count: int) -> None:
        (
            self.client.table("usage_monthly")
            .update({"count": count, "updated_at": datetime.now(timezone.utc).isoformat()})
            .eq("user_id", user_id)
            .eq("month", month)
            .execute()
        )

    def insert_post(self, user_id: str, keyword: str, tone: str, length: int, content: str) -> None:
        payload = {
            "user_id": user_id,
            "keyword": keyword,
            "tone": tone,
            "length": length,
            "content": content,
        }
        self.client.table("posts").insert(payload).execute()


def current_month_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")
