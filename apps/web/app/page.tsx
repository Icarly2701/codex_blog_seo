"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { Session } from "@supabase/supabase-js";

import { supabase } from "../lib/supabase";

type PostItem = {
  id: string;
  keyword: string;
  tone: string | null;
  length: number | null;
  content: string;
  created_at: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.API_BASE_URL;

export default function HomePage() {
  const [session, setSession] = useState<Session | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [keyword, setKeyword] = useState("");
  const [tone, setTone] = useState("전문적이지만 이해하기 쉽게");
  const [length, setLength] = useState(2000);
  const [content, setContent] = useState("");
  const [history, setHistory] = useState<PostItem[]>([]);
  const [usageMessage, setUsageMessage] = useState("무료 플랜: 월 3회 생성 제한");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const canGenerate = useMemo(() => keyword.trim().length > 0 && !loading, [keyword, loading]);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session ?? null);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
    });

    return () => listener.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (session?.access_token) {
      void fetchPosts(session.access_token);
    } else {
      setHistory([]);
    }
  }, [session?.access_token]);

  async function signUpWithEmail() {
    setError("");
    const { error: signUpError } = await supabase.auth.signUp({ email, password });
    if (signUpError) {
      setError(signUpError.message);
      return;
    }
    setUsageMessage("이메일 인증이 필요한 설정일 수 있습니다. 인증 후 로그인하세요.");
  }

  async function signInWithEmail() {
    setError("");
    const { error: signInError } = await supabase.auth.signInWithPassword({ email, password });
    if (signInError) {
      setError(signInError.message);
    }
  }

  async function signOut() {
    await supabase.auth.signOut();
  }

  async function fetchPosts(token: string) {
    if (!apiBaseUrl) {
      setError("API_BASE_URL이 설정되지 않았습니다.");
      return;
    }

    const response = await fetch(`${apiBaseUrl}/v1/posts`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      setError(body.detail || "히스토리 조회 실패");
      return;
    }

    const data = (await response.json()) as { items: PostItem[] };
    setHistory(data.items);
  }

  async function onGenerate(event: FormEvent) {
    event.preventDefault();
    setError("");

    if (!session?.access_token) {
      setError("로그인이 필요합니다.");
      return;
    }

    if (!apiBaseUrl) {
      setError("API_BASE_URL이 설정되지 않았습니다.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/v1/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({ keyword, tone, length }),
      });

      const payload = await response.json();
      if (!response.ok) {
        setError(payload.detail || "생성 실패");
        return;
      }

      setContent(payload.content || "");
      setUsageMessage(`사용량: ${payload.usage_count}/${payload.usage_limit} (남은 횟수 ${payload.remaining})`);
      await fetchPosts(session.access_token);
    } finally {
      setLoading(false);
    }
  }

  async function copyContent() {
    if (!content) {
      return;
    }
    await navigator.clipboard.writeText(content);
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      <h1 className="text-3xl font-bold">Blog SEO Writer (MVP)</h1>
      <p className="mt-2 text-sm text-slate-600">플랜: Free / Basic / Pro (현재 Free)</p>
      <p className="mt-1 text-sm text-slate-600">{usageMessage}</p>

      {!session ? (
        <section className="mt-6 rounded-xl bg-white p-6 shadow">
          <h2 className="text-xl font-semibold">로그인 / 회원가입</h2>
          <div className="mt-4 grid gap-3">
            <input
              className="rounded border border-slate-300 px-3 py-2"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              className="rounded border border-slate-300 px-3 py-2"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <div className="flex gap-2">
              <button className="rounded bg-slate-900 px-4 py-2 text-white" onClick={signInWithEmail}>
                로그인
              </button>
              <button className="rounded bg-slate-700 px-4 py-2 text-white" onClick={signUpWithEmail}>
                회원가입
              </button>
            </div>
          </div>
        </section>
      ) : (
        <>
          <section className="mt-6 rounded-xl bg-white p-6 shadow">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">글 생성</h2>
              <button className="rounded border border-slate-300 px-3 py-1 text-sm" onClick={signOut}>
                로그아웃
              </button>
            </div>

            <form className="mt-4 grid gap-3" onSubmit={onGenerate}>
              <input
                className="rounded border border-slate-300 px-3 py-2"
                placeholder="키워드 입력"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
              />
              <input
                className="rounded border border-slate-300 px-3 py-2"
                value={tone}
                onChange={(e) => setTone(e.target.value)}
              />
              <input
                className="rounded border border-slate-300 px-3 py-2"
                type="number"
                min={500}
                max={5000}
                value={length}
                onChange={(e) => setLength(Number(e.target.value))}
              />

              <button
                className="w-fit rounded bg-blue-700 px-4 py-2 font-medium text-white disabled:opacity-60"
                type="submit"
                disabled={!canGenerate}
              >
                {loading ? "생성 중..." : "SEO 글 생성"}
              </button>
            </form>
          </section>

          <section className="mt-6 rounded-xl bg-white p-6 shadow">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">생성 결과 편집</h2>
              <button className="rounded border border-slate-300 px-3 py-1 text-sm" onClick={copyContent}>
                복사
              </button>
            </div>
            <textarea
              className="mt-3 min-h-64 w-full rounded border border-slate-300 p-3"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="생성된 마크다운이 여기에 표시됩니다."
            />
          </section>

          <section className="mt-6 rounded-xl bg-white p-6 shadow">
            <h2 className="text-xl font-semibold">히스토리</h2>
            <ul className="mt-3 grid gap-3">
              {history.map((item) => (
                <li key={item.id} className="rounded border border-slate-200 p-3">
                  <p className="text-sm text-slate-500">{new Date(item.created_at).toLocaleString()}</p>
                  <p className="font-medium">{item.keyword}</p>
                  <p className="mt-1 whitespace-pre-wrap text-sm text-slate-700">{item.content}</p>
                </li>
              ))}
              {history.length === 0 ? <li className="text-sm text-slate-500">아직 생성 기록이 없습니다.</li> : null}
            </ul>
          </section>
        </>
      )}

      {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
    </main>
  );
}
