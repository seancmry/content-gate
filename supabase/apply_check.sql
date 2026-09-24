-- The saved report, and the rule that writes a decision onto one page.
-- Run from the Supabase SQL editor, or apply as a migration.

create table if not exists public.report_rows (
  url text primary key,
  retrieval_count integer,
  citation_count integer,
  citation_rate numeric,
  mentioned_brands jsonb not null default '[]'::jsonb
);

alter table public.report_rows enable row level security;

create or replace function public.apply_check(p_content_id text, p_locale text)
returns table (content_id text, locale text, status text, block_reason text)
language plpgsql
security definer
as $$
declare
  page public.pages%rowtype;
  report public.report_rows%rowtype;
  new_status text;
  new_reason text;
begin
  select * into page
  from public.pages
  where pages.content_id = p_content_id
    and pages.locale = p_locale;

  if not found then
    raise exception 'No page for % / %', p_content_id, p_locale;
  end if;

  select * into report
  from public.report_rows
  where report_rows.url = page.url;

  if length(btrim(coalesce(page.body, ''))) = 0 then
    new_status := 'blocked';
    new_reason := 'The page has no text, so it stays held.';
  elsif coalesce(page.json_ld->>'url', '') <> page.url then
    new_status := 'blocked';
    new_reason := 'The hidden label does not match the address, so it stays held.';
  elsif report.url is null then
    new_status := 'blocked';
    new_reason := 'This address is not in the report, so it stays held.';
  elsif report.citation_rate is null then
    new_status := 'blocked';
    new_reason := 'The report lists the page, but not how often it was named, so it stays held.';
  else
    new_status := 'published';
    new_reason := null;
  end if;

  update public.pages
  set
    status = new_status,
    block_reason = new_reason,
    last_peec = case
      when report.url is null then null
      else jsonb_build_object(
        'retrieval_count', report.retrieval_count,
        'citation_count', report.citation_count,
        'citation_rate', report.citation_rate,
        'mentioned_brands', report.mentioned_brands,
        'checked_at', to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
      )
    end
  where pages.content_id = p_content_id
    and pages.locale = p_locale;

  return query
  select p_content_id, p_locale, new_status, new_reason;
end;
$$;
