# Blog SEO Writer SaaS (MVP)

한국어 블로그 SEO 글을 자동 생성하는 MVP입니다.

## Stack
- Web: Next.js (TypeScript, App Router, Tailwind)
- API: FastAPI (Python)
- Auth/DB: Supabase

## Repo Structure
- `apps/web`
- `apps/api`
- `supabase/schema.sql`
- `supabase/seed.sql`
- `.env.example`

## Environment Variables
루트 `.env.example`을 복사해 값 입력:

```bash
cp .env.example .env
```

필수 값:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` (API only)
- `OPENAI_API_KEY` (API only)
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_API_BASE_URL` (예: `http://localhost:8000`)
- `API_BASE_URL` (문서 호환용)
- `CORS_ORIGINS` (예: `http://localhost:3000`)

보안 규칙:
- `SUPABASE_SERVICE_ROLE_KEY`, `OPENAI_API_KEY`는 프론트에 노출 금지
- `NEXT_PUBLIC_*`만 브라우저 노출

## Supabase Schema 적용 (SQL Editor 방식, 기본)
1. Supabase 프로젝트 생성
2. Dashboard > SQL Editor 이동
3. `supabase/schema.sql` 전체 복사 후 실행
4. 필요 시 `supabase/seed.sql` 실행

### 포함된 스키마
- `profiles` (plan: free/basic/pro)
- `posts`
- `usage_monthly` (월별 생성 횟수, 기본 limit=3)
- 인덱스 + RLS/Policy

## API 실행
```bash
cd apps/api
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

엔드포인트:
- `GET /healthz`
- `POST /v1/generate`
- `GET /v1/posts`

인증:
- `Authorization: Bearer <supabase_access_token>`

## Web 실행
```bash
cd apps/web
npm install
npm run dev
```

기본 URL: `http://localhost:3000`

## 테스트
월 3회 제한 로직 단위 테스트:

```bash
cd apps/api
python -m unittest tests/test_usage.py
```

## 생성 포맷 정책
`POST /v1/generate` 결과는 마크다운 형식을 강제합니다:
1. 클릭 유도 제목 5개
2. 최종 제목 1개
3. 도입부
4. H2 소제목 3~5개 + 본문
5. 결론(요약 + CTA)
6. 메타 설명(150자 내외)

## 배포 가이드

### Web: Vercel
1. Vercel에 Git 리포 연결
2. Environment Variables 설정
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_BASE_URL` (배포된 API URL)
3. Deploy 후 도메인 확인
4. Supabase Auth Redirect URL 설정
   - `https://<vercel-domain>/auth/callback`

### API: Render 또는 Railway
1. `apps/api` 기준 배포
2. Start Command
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. 환경변수 설정
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL`
   - `CORS_ORIGINS` (Vercel 도메인)
4. `/healthz`로 헬스체크 확인

## CORS/도메인 체크리스트
- API `CORS_ORIGINS`에 실제 웹 도메인 포함
- Web `NEXT_PUBLIC_API_BASE_URL`이 실제 API 도메인인지 확인
- Supabase Redirect URL이 실제 Web 도메인과 일치하는지 확인

## 변경 파일 요약
- DB: `supabase/schema.sql`, `supabase/seed.sql`
- API: FastAPI 엔드포인트, Supabase/OpenAI 연동, usage 제한 로직, 테스트
- Web: Auth + 글 생성 + 편집 + 복사 + 히스토리 UI
- Ops: `.env.example`, 배포/실행 문서
