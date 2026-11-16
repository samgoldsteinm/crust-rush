-- Patch 47 (web v209): the "No items" world boards. Run once in the Supabase SQL editor, AFTER lb_schema.sql.
-- Safe on a live board: it adds a column and keeps every time already there (does NOT empty anything).
alter table public.runs add column if not exists noitems boolean not null default false;

drop view if exists public.best_runs;
create view public.best_runs as
  select distinct on (r.map, r.cls, (case when r.noitems then 'noitems' when r.solo then 'alone' else 'rivals' end), r.player_id) r.map, r.cls,
         case when r.noitems then null else r.solo end as solo, r.noitems, p.name, r.driver, r.kart, r.platform, r.time_ms, r.created_at
  from runs r join players p on p.id = r.player_id
  order by r.map, r.cls, (case when r.noitems then 'noitems' when r.solo then 'alone' else 'rivals' end), r.player_id, r.time_ms;
grant select on public.best_runs to anon;

create or replace function public.submit_run(p_token text, p_map text, p_cls text, p_time_ms int, p_driver text, p_kart text, p_platform text, p_ver text, p_solo boolean, p_noitems boolean)
returns void language plpgsql security definer set search_path = public as $$
declare pid bigint;
begin
  select id into pid from players where token_hash = hash_token(p_token);
  if pid is null then raise exception 'no player'; end if;
  insert into runs (player_id, map, cls, time_ms, driver, kart, platform, ver, solo, noitems)
    values (pid, p_map, p_cls, p_time_ms, p_driver, p_kart, p_platform, p_ver, p_solo, p_noitems);
end $$;
grant execute on function public.submit_run(text, text, text, int, text, text, text, text, boolean, boolean) to anon;
create index if not exists runs_board_ni on public.runs (map, cls, noitems, solo, time_ms);
