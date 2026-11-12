# Crust Rush: source and tools (branch `source`)

This branch is the working source of the web game and the tools that build and test it. The published game is on
branch `main` (built output, served by GitHub Pages); the Windows PC version is on branch `godot`.

**Read `docs/HANDOVER.md` first**: what has broken before, why, and what fixed it. `docs/MINIATURE-MAYHEM-PLAN.md`
holds the working notes for the toy-track cup (layout numbers, scale, what is done and what is next).

## What is here
- `crust-rush.html`: the whole web game in one file (code, models, textures and menu pictures embedded).
- `build/`: `build_gh.py` splits the source into the app that is published on `main` (it runs `extract.js`, uses
  `sw_tmpl.js`, the replacement pictures in `hq/`, and the three.js files in `vendor/`).
- `tools/neon/`: track layout tool (`gen.py`), the Neon Cup's layouts and scenery code (`neon.js`), and the test
  scripts: `webtest.sh` (syntax check + build + test copy), `boottest.py`, `loadtest.py`, `simtest.py` (self-driving
  race), `shots.py` (free camera pictures), `chase.py` (the game's own camera), `embed_shots.py`.
- `tools/mini/`: the Miniature Mayhem cup: room and toy-set code (`mini.js`), the furniture model library
  (`models.js`), the Bedroom Blitz layout (`t_bedroom.py`), `inject_mini.py` (puts them into the source), the
  one-off engine patches (already applied to the source), and the model viewer (`view/viewer.html`, `view.py`).

## Paths
The scripts were written in a cloud workspace and use absolute paths: the source at `/home/claude/crust-rush.html`,
the app checkout at `/home/claude/crust-rush-app`, tools at `/home/claude/neon` and `/home/claude/mini`, build inputs
at `/tmp/claude-0/gh`, three.js at `/tmp/claude-0/t/threejs/build` and `/tmp/claude-0/three-new/build`, and a scratch
folder for test output. On another machine, change those paths at the top of each script (or recreate the layout).
The tests need Python with Playwright and Pillow, Node, and a Chromium that Playwright can launch.

## Publishing a web update
1. Edit `crust-rush.html` (or the files in `tools/mini` and run `inject_mini.py`).
2. `tools/neon/webtest.sh` builds the app with the version stamp written in that script; bump the stamp after each release.
3. Run the checks listed at the end of `docs/HANDOVER.md`.
4. Commit and push the built app on `main`; commit the changed source here.
5. If tracks or karts changed, the PC build needs its track export re-run (see `docs/HANDOVER.md`).
