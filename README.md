# Crust Rush

A 3D kart racer on giant pizzas. Three tracks with hills, ramps and a loop-the-loop, eight drivers, CPU difficulty levels, drifting, items and boosts.

## Play

Once GitHub Pages is on, the game lives at:

`https://samgoldsteinm.github.io/crust-rush/`

## Install it like an app

- **iPhone or iPad (Safari):** open the link, tap the Share button, then **Add to Home Screen**.
- **Android (Chrome):** open the link, tap the menu (⋮), then **Install app** or **Add to Home screen**.
- **Computer (Chrome or Edge):** open the link and click the install icon in the address bar.

The installed app opens full screen with no browser bars. After the first visit it also works offline.

## Controls

- Touch the left or right half of the screen to steer.
- Tap a Drift button (bottom corners) at speed to start drifting. Steer to guide it, and tap again for a boost. When slow, hold it to brake or reverse.
- Tap the item button to throw ahead, or swipe down on it to throw behind.
- Keyboard: arrows steer, Space drifts, X throws ahead, Z throws back, P pauses.

## Files

- `index.html`: the whole game
- `manifest.webmanifest`: app name, icons and full-screen landscape settings
- `sw.js`: offline support
- `icons/`: app icons

## Updating

Replace `index.html` with a new version and push. When you ship an update, change `VERSION` at the top of `sw.js` (for example `crust-rush-v2`) so installed copies pick up the new files.
