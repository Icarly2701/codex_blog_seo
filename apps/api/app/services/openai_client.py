from fastapi import HTTPException, status
from openai import OpenAI

from app.config import settings


def _build_prompt(keyword: str, tone: str, length: int) -> str:
    return f"""
다음 조건을 모두 만족하는 한국어 SEO 블로그 글을 작성하세요.

입력:
- 키워드: {keyword}
- 톤: {tone}
- 목표 길이: 약 {length}자

출력 형식(반드시 마크다운):
1) 클릭 유도 제목 5개
2) 최종 제목 1개
3) 도입부
4) H2 소제목 3~5개 + 각 섹션 내용
5) 결론(요약 + CTA)
6) 메타 설명(150자 내외)

주의사항:
- 출처 없는 숫자/통계는 단정하지 말 것
- 의료/법률/재무 등 고위험 조언은 일반 정보임을 명시하고 전문가 상담 권장 문구 포함
""".strip()


def generate_markdown(keyword: str, tone: str, length: int) -> str:
    provider = settings.llm_provider.lower().strip()
    if provider == "groq":
        if not settings.groq_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GROQ_API_KEY is missing",
            )
        client = OpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1")
        model = settings.groq_model
    else:
        if not settings.openai_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OPENAI_API_KEY is missing",
            )
        client = OpenAI(api_key=settings.openai_api_key)
        model = settings.openai_model

    prompt = _build_prompt(keyword=keyword, tone=tone, length=length)

    completion = client.chat.completions.create(
        model=model,
        temperature=0.7,
        messages=[
            {"role": "system", "content": "당신은 한국어 SEO 전문 작가입니다."},
            {"role": "user", "content": prompt},
        ],
    )

    return completion.choices[0].message.content or ""
