# 專案初始化用的 Supabase schema。
SCHEMA_SQL = """
create extension if not exists "pgcrypto";

create table if not exists public.analysis_runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  query text not null,
  analyzed_at timestamptz not null default now(),
  article_count integer not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.analysis_articles (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references public.analysis_runs(id) on delete cascade,
  rank integer not null,
  title text not null,
  url text not null,
  snippet text not null default '',
  total_entity_mentions integer not null default 0,
  unique_entity_count integer not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.analysis_entities (
  id uuid primary key default gen_random_uuid(),
  article_id uuid not null references public.analysis_articles(id) on delete cascade,
  name text not null,
  entity_type text not null,
  mentions integer not null default 0,
  salience numeric not null default 0,
  created_at timestamptz not null default now()
);
"""


if __name__ == "__main__":
    # 直接印出 SQL，方便貼到 Supabase SQL Editor。
    print(SCHEMA_SQL)
