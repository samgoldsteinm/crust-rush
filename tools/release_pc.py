"""Bring the PC version level with the published web game: re-export the tracks, then build. Takes about an hour; run it in
the background. usage: py.cmd tools/release_pc.py "<what changed, one line>" ["<more lines>"]
The order matters (docs/HANDOVER.md): web is published first; the export runs from the published web game; the PC build must
start only after the export has finished and no other PC build is running.
What it does:
  1. commits tools/glbexport.js, tools/ci*.py and the note in maps.yml as "[quick]" and pushes: that starts the export only
  2. waits until the export has succeeded and no PC build is running
  3. commits every other change in D:/crust-rush/godot, plus web_rev.txt (so there is always something to build), and pushes
  4. waits for that build and prints the public download's stamp
"""
import json, re, subprocess, sys, time, urllib.request
R = 'D:/crust-rush'
API = 'https://api.github.com/repos/samgoldsteinm/crust-rush/actions/runs?branch=godot&per_page=10'
TAIL = '\n\nCo-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01M2eKvptTQwPcovHKAgrKmo\n'


def git(*a, check=True):
    r = subprocess.run(['git', '-C', f'{R}/godot', *a], capture_output=True, text=True, encoding='utf-8')
    if check and r.returncode: sys.exit(f'git {" ".join(a)} failed:\n{r.stdout}{r.stderr}')
    return r.stdout.strip()


def runs():
    for _ in range(5):
        try:
            return json.load(urllib.request.urlopen(API, timeout=30)).get('workflow_runs', [])
        except Exception as e:
            print('  (GitHub did not answer:', str(e)[:80], ')', flush=True); time.sleep(60)
    return []


def wait(what, sha, extra_idle=False, minutes=90):
    for _ in range(minutes):
        rs = runs(); mine = [r for r in rs if r['name'] == what and r['head_sha'].startswith(sha)]
        busy = [r for r in rs if r['name'] == 'PC build' and r['status'] != 'completed' and not r['head_sha'].startswith(sha)]
        if mine and mine[0]['status'] == 'completed' and not (extra_idle and busy):
            if mine[0]['conclusion'] != 'success': sys.exit(f'{what} for {sha} ended as {mine[0]["conclusion"]}: nothing more was pushed')
            return
        time.sleep(60)
    sys.exit(f'gave up waiting for {what} {sha}')


title = sys.argv[1]; body = '\n'.join(sys.argv[2:])
web = json.load(urllib.request.urlopen('https://samgoldsteinm.github.io/crust-rush/version.json', timeout=30))['build'].replace('crust-rush-', '')
local = re.search(r"v(\d+)", open(f'{R}/app/version.json').read()).group(0)
if web != local: sys.exit(f'the live web game is {web} but the local app is {local}: wait for GitHub Pages, then run again')
# 1. the export
my = f'{R}/godot/.github/workflows/maps.yml'
s = open(my, encoding='utf-8', newline='').read()
s = re.sub(r'# \(Last run for: [^\n]*\)', f'# (Last run for: web {web}, {title}.)', s, count=1)
open(my, 'w', encoding='utf-8', newline='').write(s)
git('add', '.github/workflows/maps.yml', 'tools/glbexport.js', 'tools/ciexport.py', 'tools/cigarage.py')
git('commit', '-q', '-m', f'Re-export the tracks for web {web} [quick]{TAIL}')
git('fetch', '-q', 'origin'); git('merge-base', '--is-ancestor', 'origin/godot', 'HEAD'); git('push', '-q', 'origin', 'HEAD:godot')
ex = git('log', '--format=%H', '-1'); print('export started', ex[:7], flush=True)
time.sleep(40); wait('Export tracks', ex[:7], extra_idle=True); print('export done', flush=True)
# 2. the build
open(f'{R}/godot/web_rev.txt', 'w', encoding='utf-8', newline='').write(f'The room and track data in this build come from web {web}.\n')
git('add', '-A'); git('commit', '-q', '-m', f'PC: {title} (as web {web})' + ('\n\n' + body if body else '') + TAIL)
git('fetch', '-q', 'origin'); git('merge-base', '--is-ancestor', 'origin/godot', 'HEAD'); git('push', '-q', 'origin', 'godot')
pc = git('log', '--format=%H', '-1'); print('build started', pc[:7], flush=True)
time.sleep(40); wait('PC build', pc[:7]); print('build done', flush=True)
print(urllib.request.urlopen('https://github.com/samgoldsteinm/crust-rush/releases/download/pc/pc-build.json', timeout=60).read().decode()[:120])
