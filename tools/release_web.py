"""Publish the built web game and bump the version stamp.
usage: py.cmd tools/release_web.py "<one-line title>" ["<more lines for the log>"]
Before running: the checks in docs/HANDOVER.md have passed on the build that is in D:/crust-rush/app (webtest.py made it).
What it does, in order:
  1. commits everything in `source` as "Web vN source: <title>" and pushes it
  2. commits the built app as "Web vN: <title>" (with the extra lines) and pushes `main` after checking nobody else pushed
  3. bumps the stamp in tools/neon/webtest.py to vN+1, commits and pushes that
The second site (build/asset_site.json; repository crust-rush-assets, checked out at D:/crust-rush/assets) goes first: its new files are
committed and pushed before step 2, and when the game uses that site ("on": true) step 2 waits until every one of this build's files
answers there, so the game is never published pointing at a file that is not up yet. After step 2 the files of builds older than the
previous one are removed from it.
"""
import json, os, re, subprocess, sys, time, urllib.request
R = 'D:/crust-rush'
TAIL = '\n\nCo-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01M2eKvptTQwPcovHKAgrKmo\n'


def git(repo, *a, check=True):
    r = subprocess.run(['git', '-C', f'{R}/{repo}', *a], capture_output=True, text=True, encoding='utf-8')
    if check and r.returncode: sys.exit(f'git {" ".join(a)} failed in {repo}:\n{r.stdout}{r.stderr}')
    return r.stdout.strip()


title = sys.argv[1]; body = '\n'.join(sys.argv[2:])
wt = f'{R}/source/tools/neon/webtest.py'
src = open(wt, encoding='utf-8', newline='').read()
n = int(re.search(r"VERSION = 'crust-rush-v(\d+)'", src).group(1))
sw = open(f'{R}/app/sw.js', encoding='utf-8').read()
if f'crust-rush-v{n}' not in sw: sys.exit(f'the built app is not v{n}: run webtest.py first')
if git('source', 'status', '--short'):
    git('source', 'add', '-A'); git('source', 'commit', '-q', '-m', f'Web v{n} source: {title}{TAIL}')
git('source', 'fetch', '-q', 'origin'); git('source', 'merge-base', '--is-ancestor', 'origin/source', 'HEAD'); git('source', 'push', '-q', 'origin', 'source')
if not git('app', 'status', '--short'): sys.exit('nothing to publish: the app is unchanged')
# ---- the second site first
AS = json.load(open(f'{R}/source/build/asset_site.json', encoding='utf-8')); AD = AS['dir']; HAVE = os.path.isdir(AD + '/.git')
def assets_push(msg):
    if not git('assets', 'status', '--short'): return False
    git('assets', 'add', '-A'); git('assets', 'commit', '-q', '-m', msg + TAIL); git('assets', 'fetch', '-q', 'origin')
    if git('assets', 'ls-remote', '--heads', 'origin', 'main'): git('assets', 'merge-base', '--is-ancestor', 'origin/main', 'HEAD')
    git('assets', 'push', '-q', 'origin', 'HEAD:main'); return True
def answers(url):
    try: return urllib.request.urlopen(urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'release-check'}), timeout=20).status == 200
    except Exception: return False
if HAVE:
    cur = json.load(open(AD + '/current.json'))
    if cur['build'] != f'crust-rush-v{n}': sys.exit(f"the second site's file list is for {cur['build']}, not v{n}: run webtest.py first")
    if assets_push(f'Files for web v{n}'): print('second site: new files pushed')
    if AS['on']:
        todo = list(cur['files']); t0 = time.time()
        while todo and time.time() - t0 < 900:
            todo = [f for f in todo if not answers(AS['abs'] + f)]
            if todo: time.sleep(20)
        if todo: sys.exit(f'{len(todo)} files are not answering on the second site after 15 minutes (first: {todo[0]}): the game is NOT published. Is Pages on for that repository?')
        print('second site: all', len(cur['files']), 'files answer')
git('app', 'add', '-A'); git('app', 'commit', '-q', '-m', f'Web v{n}: {title}' + ('\n\n' + body if body else '') + TAIL)
git('app', 'fetch', '-q', 'origin'); git('app', 'merge-base', '--is-ancestor', 'origin/main', 'HEAD'); git('app', 'push', '-q', 'origin', 'main')
open(wt, 'w', encoding='utf-8', newline='').write(src.replace(f"VERSION = 'crust-rush-v{n}'", f"VERSION = 'crust-rush-v{n + 1}'"))
git('source', 'add', '-A'); git('source', 'commit', '-q', '-m', f'Web v{n} is published; next stamp v{n + 1}{TAIL}'); git('source', 'push', '-q', 'origin', 'source')
print(f'published web v{n}:', git('app', 'log', '--oneline', '-1'))
if HAVE:   # tidy the second site: keep this build's files and the build before's (a page still open on the old version keeps working)
    pj = AD + '/published.json'; prev = json.load(open(pj))['files'] if os.path.exists(pj) else []; keep = set(cur['files']) | set(prev); gone = 0
    for kind in ('geo', 'tex'):
        for fn in (os.listdir(f'{AD}/{kind}') if os.path.isdir(f'{AD}/{kind}') else []):
            if f'{kind}/{fn}' not in keep: os.remove(f'{AD}/{kind}/{fn}'); gone += 1
    json.dump({'build': cur['build'], 'files': cur['files']}, open(pj, 'w', newline=''), indent=0)
    assets_push(f'Web v{n} is published: its file list' + (f'; {gone} older files removed' if gone else ''))
    asz = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(AD) if '.git' not in d.replace(os.sep, '/').split('/') for f in fs)
    print(f"second site: {asz / 1e6:.0f} MB of 1024, {'IN USE by the game' if AS['on'] else 'published but not used by the game yet'}")
# how much room is left: GitHub Pages serves a site of at most 1 GB, and asks that a repository stay under about 1 GB too
site = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(f'{R}/app') if '.git' not in d.replace(os.sep, '/').split('/') for f in fs)
try: repo = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.github.com/repos/samgoldsteinm/crust-rush', headers={'User-Agent': 'release-check'}), timeout=20).read())['size'] / 1024
except Exception: repo = None
print(f'space: the site is {site / 1e6:.0f} MB of 1024' + (f'; the repository is {repo:.0f} MB on GitHub (keep under 1000)' if repo else ''))
if site > 700e6 or (repo or 0) > 800: print('SPACE WARNING: time to move the late-loading models and big textures to a second repository (docs/HANDOVER.md, "Space")')

