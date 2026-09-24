-- Plain tables for the Supabase table view.
-- articles: the eight stored pages.
-- checks: all fourteen results, including the demo-only ones.

create table if not exists public.checks (
  id bigint generated always as identity primary key,
  page_name text not null,
  language text not null,
  address text not null,
  saved_where text not null,
  how_often_named numeric,
  decision text not null,
  why text not null
);

create table if not exists public.articles (
  page_name text not null,
  language text not null,
  address text not null,
  body text not null,
  decision text not null,
  why text,
  primary key (page_name, language)
);

alter table public.checks enable row level security;
alter table public.articles enable row level security;
