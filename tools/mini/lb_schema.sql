-- The world leaderboard's database (Supabase, the owner's project), as the owner ran it on 2026-11-16 in the SQL editor.
-- Running it again EMPTIES the board (it drops the tables first). See docs/HANDOVER.md, "usernames and the world leaderboard".
drop view if exists public.best_runs;
drop table if exists public.runs;
drop table if exists public.players;
create extension if not exists pgcrypto;

create table public.players (
  id bigint generated always as identity primary key,
  name text not null check (name ~ '^[A-Za-z0-9_ .-]{3,16}$'),
  token_hash text not null unique,
  created_at timestamptz not null default now()
);
create unique index players_name on public.players (lower(name));

create table public.runs (
  id bigint generated always as identity primary key,
  player_id bigint not null references public.players(id) on delete cascade,
  map text not null check (char_length(map) between 1 and 24),
  cls text not null check (cls in ('easy','medium','hard','mirror')),
  solo boolean not null default false,
  time_ms integer not null check (time_ms between 20000 and 1800000),
  driver text not null check (char_length(driver) between 1 and 16),
  kart text not null check (char_length(kart) between 1 and 32),
  platform text not null check (platform in ('web','pc')),
  ver text not null check (char_length(ver) <= 16),
  created_at timestamptz not null default now()
);
create index runs_board on public.runs (map, cls, solo, time_ms);
alter table public.players enable row level security;
alter table public.runs enable row level security;

create or replace function public.hash_token(t text) returns text language sql immutable
  as $$ select encode(extensions.digest(t, 'sha256'), 'hex') $$;

create or replace function public.name_free(p_name text) returns boolean language sql security definer set search_path = public
  as $$ select not exists (select 1 from players where lower(name) = lower(trim(p_name))) $$;

create or replace function public.claim_name(p_token text, p_name text) returns text language plpgsql security definer set search_path = public as $$
begin
  if char_length(p_token) < 32 then raise exception 'bad token'; end if;
  update players set name = trim(p_name) where token_hash = hash_token(p_token);
  if not found then insert into players (name, token_hash) values (trim(p_name), hash_token(p_token)); end if;
  return trim(p_name);
exception when unique_violation then raise exception 'name taken';
end $$;

create or replace function public.whoami(p_token text) returns text language sql security definer set search_path = public
  as $$ select name from players where token_hash = hash_token(p_token) $$;

create or replace function public.submit_run(p_token text, p_map text, p_cls text, p_time_ms int, p_driver text, p_kart text, p_platform text, p_ver text, p_solo boolean)
returns void language plpgsql security definer set search_path = public as $$
declare pid bigint;
begin
  select id into pid from players where token_hash = hash_token(p_token);
  if pid is null then raise exception 'no player'; end if;
  insert into runs (player_id, map, cls, time_ms, driver, kart, platform, ver, solo)
    values (pid, p_map, p_cls, p_time_ms, p_driver, p_kart, p_platform, p_ver, p_solo);
end $$;

create view public.best_runs as
  select distinct on (r.map, r.cls, r.solo, r.player_id) r.map, r.cls, r.solo, p.name, r.driver, r.kart, r.platform, r.time_ms, r.created_at
  from runs r join players p on p.id = r.player_id
  order by r.map, r.cls, r.solo, r.player_id, r.time_ms;

revoke all on public.players, public.runs from anon, authenticated;
grant select on public.best_runs to anon;
grant execute on function public.name_free(text), public.claim_name(text, text), public.whoami(text),
  public.submit_run(text, text, text, int, text, text, text, text, boolean) to anon;
