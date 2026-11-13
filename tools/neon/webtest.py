"""Build the web game and make a hooked test copy served on port 8771 (replaces webtest.sh on the PC).
usage: webtest.py            build with the version stamp below
The stamp is the NEXT version to publish: bump it straight after each release."""
import glob, os, shutil, socket, subprocess, sys
VERSION = 'crust-rush-v161'
R = 'D:/crust-rush'
SRC, APP, SP = R + '/source/crust-rush.html', R + '/app', R + '/scratch'
NODE = R + '/tools/node/node.exe'
env = dict(os.environ, PYTHONUTF8='1', PATH=R + '/tools/node;' + os.environ['PATH'])
# 1. every inline script must parse
chk = "const s=require('fs').readFileSync(process.argv[1],'utf8');for(const x of s.matchAll(/<script(?![^>]*src)[^>]*>([\\s\\S]*?)<\\/script>/g)){new Function(x[1]);}"
subprocess.run([NODE, '-e', chk, SRC], check=True)
# 2. build the app
subprocess.run([sys.executable, R + '/source/build/build_gh.py', VERSION], check=True, env=env, stdout=subprocess.DEVNULL)
# 3. a copy with a hook (window.__ev) for the test scripts
dst = SP + '/webcopy6'
shutil.rmtree(dst, ignore_errors=True)
shutil.copytree(APP, dst, ignore=shutil.ignore_patterns('.git'))
f = glob.glob(dst + '/js/game.*.js')[0]
s = open(f, encoding='utf-8', newline='').read()
i = s.rindex('})();')
open(f, 'w', encoding='utf-8', newline='').write(s[:i] + 'window.__ev=(x)=>eval(x);' + s[i:])
# 4. the test server
def up():
    c = socket.socket()
    try:
        c.settimeout(.5); c.connect(('127.0.0.1', 8771)); return True
    except OSError:
        return False
    finally:
        c.close()
if not up():
    subprocess.Popen([sys.executable, '-m', 'http.server', '8771', '--directory', SP], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=getattr(subprocess, 'DETACHED_PROCESS', 0) | getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
print('built', VERSION)
