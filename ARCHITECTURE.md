# Blog SEO Writer SaaS - Current Architecture

이 문서는 `codex_blog_seo` 프로젝트의 현재 동작 구조를 전체적으로 설명합니다.

## 1. 전체 개요

이 프로젝트는 한국어 SEO 블로그 글 생성을 위한 MVP입니다.

- Web: Next.js (Vercel)
- API: FastAPI (Render)
- Auth/DB: Supabase
- LLM: OpenAI 또는 Groq(OpenAI-compatible)

현재 배포 URL:
- Web: `https://codex-blog-seo-web.vercel.app/`
- API: `https://blog-seo-api.onrender.com`

## 2. 디렉터리 구조

```txt
blog-seo-saas/
  apps/
    api/
      app/
        main.py
        config.py
        auth.py
        schemas.py
        services/
          openai_client.py
          supabase_client.py
          usage.py
      tests/
        test_usage.py
      requirements.txt
      Dockerfile
    web/
      app/
        page.tsx
        layout.tsx
        globals.css
        auth/callback/route.ts
      lib/
        supabase.ts
      package.json
      tsconfig.json
      next.config.ts
      tailwind.config.ts
      postcss.config.js
  supabase/
    schema.sql
    seed.sql
  render.yaml
  vercel.json
  .env.example
  README.md
  package.json
```

## 3. 아키텍처 흐름

### 3.1 인증 흐름

1. 사용자가 Web에서 이메일/비밀번호로 회원가입/로그인
2. Web이 Supabase Auth를 통해 세션(access token) 획득
3. Web이 API 호출 시 `Authorization: Bearer <token>` 전달
4. API가 Supabase `auth.get_user(token)`로 사용자 식별

### 3.2 글 생성 흐름

1. Web에서 키워드/톤/길이 입력
2. `POST /v1/generate` 호출
3. API에서 월별 사용량(`usage_monthly`) 조회
4. 월 3회 제한 검사
5. LLM(OpenAI 또는 Groq) 호출하여 마크다운 생성
6. `posts` 저장 + `usage_monthly.count` 증가
7. Web에 생성 결과/남은 횟수 반환

### 3.3 히스토리 조회 흐름

1. Web이 `GET /v1/posts` 호출
2. API가 현재 사용자 `posts`만 조회
3. Web에서 리스트 렌더링

## 4. 백엔드(API) 구성

### 4.1 엔드포인트

- `GET /healthz`
  - 상태 점검용, `{"status":"ok"}` 반환
- `GET /v1/posts`
  - 로그인 사용자 글 목록 반환
- `POST /v1/generate`
  - 생성 + 사용량 제한 + 저장

### 4.2 핵심 파일

- `apps/api/app/main.py`
  - FastAPI 앱, CORS, 라우팅
- `apps/api/app/config.py`
  - 환경변수 로딩
- `apps/api/app/auth.py`
  - Bearer 토큰 파싱/검증 전처리
- `apps/api/app/services/supabase_client.py`
  - Supabase 테이블/유저 연동
- `apps/api/app/services/usage.py`
  - 월간 제한 로직 (순수 함수)
- `apps/api/app/services/openai_client.py`
  - LLM 호출 (provider 전환 포함)

### 4.3 LLM Provider 전략

`config.py` 기준:
- `LLM_PROVIDER=openai` -> `OPENAI_API_KEY`, `OPENAI_MODEL` 사용
- `LLM_PROVIDER=groq` -> `GROQ_API_KEY`, `GROQ_MODEL` 사용

`openai_client.py`에서
- Groq 사용 시 `base_url="https://api.groq.com/openai/v1"`로 OpenAI SDK 재사용

## 5. 프론트엔드(Web) 구성

### 5.1 핵심 파일

- `apps/web/app/page.tsx`
  - 로그인/회원가입 UI
  - 생성 폼
  - 결과 textarea + 복사
  - 히스토리 렌더링
  - 사용자 친화적 에러 메시지 매핑
- `apps/web/lib/supabase.ts`
  - Supabase client 생성

### 5.2 Web 동작 포인트

- API URL은 `NEXT_PUBLIC_API_BASE_URL` 사용
- trailing slash 제거 처리 (`https://.../` -> `https://...`)
  - `//v1/generate` 문제 방지
- 회원가입 시
  - 이메일 형식/비밀번호 길이 사전 검증
  - 자주 발생하는 Supabase 에러를 안내 문구로 변환

## 6. DB(Supabase) 스키마

파일: `supabase/schema.sql`

테이블:
- `profiles` (user plan)
- `posts` (생성 결과 저장)
- `usage_monthly` (월별 횟수 제한)

정책:
- RLS 활성화
- `posts`는 본인 데이터만 select/insert
- `usage_monthly`는 본인 row select
- `profiles`는 본인 row select/insert/update

주의:
- Supabase PostgreSQL은 `create policy if not exists` 미지원
- 현재 파일은 `drop policy if exists + create policy` 방식으로 호환 처리

## 7. 환경변수 정리

파일: `.env.example`

필수/주요 변수:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `LLM_PROVIDER` (`openai` or `groq`)
- `OPENAI_API_KEY`, `OPENAI_MODEL`
- `GROQ_API_KEY`, `GROQ_MODEL`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_API_BASE_URL`
- `CORS_ORIGINS`

보안 규칙:
- 서버 전용 키: `SUPABASE_SERVICE_ROLE_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`
- 프론트 노출 허용: `NEXT_PUBLIC_*`만

## 8. 배포 구성

### 8.1 Vercel (Web)

- 설정 파일: `vercel.json`
- 실제 Root Directory는 Vercel 프로젝트 설정에서 `apps/web`
- env:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `NEXT_PUBLIC_API_BASE_URL=https://blog-seo-api.onrender.com`

### 8.2 Render (API)

- 설정 파일: `render.yaml`
- Docker 기반 배포 (`apps/api/Dockerfile`)
- env:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `CORS_ORIGINS=https://codex-blog-seo-web.vercel.app`
  - `LLM_PROVIDER=groq` (권장)
  - `GROQ_API_KEY`
  - `GROQ_MODEL=llama-3.1-8b-instant`

## 9. 테스트/검증

### 9.1 로컬 검증

- API 단위 테스트:
  - `cd apps/api && python -m unittest tests/test_usage.py`
- API 헬스체크:
  - `GET /healthz`
- Web 빌드:
  - `cd apps/web && npm run build`

### 9.2 배포 후 검증

1. Web 접속/로그인
2. 글 생성 1회 성공
3. 히스토리 조회 성공
4. 4번째 생성 시 429 제한 확인

## 10. 최근 이슈와 해결 기록

1. Vercel Next 취약버전 차단
- 원인: `next@15.1.6`
- 해결: `15.5.12` 업그레이드

2. Render 시작 오류 (`Path.parents[3]`)
- 원인: 런타임 경로 가정
- 해결: `.env` 로딩 방식 단순화

3. CORS 차단
- 원인: `CORS_ORIGINS` 불일치
- 해결: `https://codex-blog-seo-web.vercel.app` 정확히 설정

4. `//v1/generate` 호출
- 원인: API base URL trailing slash
- 해결: Web에서 trailing slash 제거

5. Supabase policy SQL 문법 오류
- 원인: `create policy if not exists` 미지원
- 해결: `drop policy if exists + create policy`

6. OpenAI 429 insufficient_quota
- 원인: API 크레딧 부족
- 해결: Groq provider 지원 추가

## 11. 현재 운영 체크리스트

- [ ] Supabase SQL(`supabase/schema.sql`) 적용 완료
- [ ] Render env `SUPABASE_*` 정확
- [ ] Render env `LLM_PROVIDER=groq` + `GROQ_API_KEY` 설정
- [ ] Render env `CORS_ORIGINS` 정확
- [ ] Vercel env `NEXT_PUBLIC_API_BASE_URL` 정확
- [ ] 회원가입/로그인 성공
- [ ] 생성/히스토리/월 제한 동작

