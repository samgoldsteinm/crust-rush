# Crust Rush

A 3D kart racer on giant pizzas, made as an installable web app. Sixteen tracks in four Grand Prix cups, speed classes from 50cc to Reverse, 25 items, eight drivers with their own special abilities, a soundtrack for every track, moving hazards, and a garage where you build your kart from bodies, wheels, gliders, colours and liveries.

**Play:** https://samgoldsteinm.github.io/crust-rush/

## Controls

- Touch the left or right half of the screen to steer.
- Tap a Drift button at speed to start drifting; steer to guide it and tap again for a boost. When slow, hold it to brake or reverse.
- Your two item slots sit top right; tap either one to use that item. Traps drop onto the road behind you; everything else fires forward. Garlic shields stay on until you are hit. The button top left is your driver's special ability, ready every 30 seconds.
- Keyboard: arrows steer, Space drifts, X throws ahead, Z or V uses the second item, C uses the ability, P or Esc pauses. Settings has a full guide to every item and special ability.

## Install it like an app

- **iPhone or iPad (Safari):** open the link, tap the Share button, then **Add to Home Screen**.
- **Android (Chrome):** open the link, tap the **⋮** menu, then **Install app** (or **Add to Home screen**).
- **Computer (Chrome or Edge):** open the link and click the install icon at the right end of the address bar.

After the first visit the game is saved on your device and works offline. It opens full screen with no browser bars.

## How the files are laid out

| Path | What it holds |
| --- | --- |
| `index.html` | The page and its menus |
| `js/game.<hash>.js` | The game itself |
| `css/style.<hash>.css` | All styling |
| `vendor/three-0.149.0.min.js` | The 3D engine (three.js) |
| `assets/geo.<hash>.bin` | Every car and scenery model, packed into one download |
| `assets/tex/` | Sky panoramas and scenery textures |
| `assets/shots/` | Track photos for the menus |
| `sw.js` | Offline support: saves every file above on the device |

Files with a hash in the name get a new name whenever their contents change, so an update can never mix old and new pieces. Unchanged files keep their names, so each update only adds the files that actually changed.

## Updating

All files are generated from one source file by a build script, so replace them as a set and commit everything together. The `crust-rush-vNN` version in `sw.js` goes up with every release, which tells installed copies to fetch the new files.

## Credits

Some 3D models and sky images are used under Creative Commons Attribution licences; the full list is in the game's **How to play** screen.
