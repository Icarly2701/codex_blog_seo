create extension if not exists pgcrypto;

create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  plan text not null default 'free' check (plan in ('free', 'basic', 'pro')),
  created_at timestamptz not null default now()
);

create table if not exists public.posts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  keyword text not null,
  tone text,
  length int,
  content text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.usage_monthly (
  user_id uuid not null references auth.users(id) on delete cascade,
  month text not null,
  count int not null default 0,
  "limit" int not null default 3,
  updated_at timestamptz not null default now(),
  primary key (user_id, month)
);

create index if not exists idx_posts_user_created_at
  on public.posts(user_id, created_at desc);

create index if not exists idx_usage_monthly_user_month
  on public.usage_monthly(user_id, month);

alter table public.posts enable row level security;
alter table public.usage_monthly enable row level security;
alter table public.profiles enable row level security;

drop policy if exists "posts_select_own" on public.posts;
create policy "posts_select_own"
  on public.posts
  for select
  using (auth.uid() = user_id);

drop policy if exists "posts_insert_own" on public.posts;
create policy "posts_insert_own"
  on public.posts
  for insert
  with check (auth.uid() = user_id);

drop policy if exists "usage_select_own" on public.usage_monthly;
create policy "usage_select_own"
  on public.usage_monthly
  for select
  using (auth.uid() = user_id);

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own"
  on public.profiles
  for select
  using (auth.uid() = user_id);

drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own"
  on public.profiles
  for insert
  with check (auth.uid() = user_id);

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own"
  on public.profiles
  for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);
