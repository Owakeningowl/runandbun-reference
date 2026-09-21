# Run and Bun — Reference Site

Four pages, one theme, cross-linked:

| Page | File | Notes |
|---|---|---|
| AI Reference | `index.html` | Croven's RnB AI doc. Self-contained. |
| Trainers | `trainers.html` | 436 trainers, 1832 Pokémon. Sprites load from PokeAPI. |
| Dex | `dex.html` | Mirror of [RBDex](https://may8th1995.github.io/RBDex/) — needs the network. |
| Calc | `calc.html` | Mirror of [dekzeh's calc](https://dekzeh.github.io/calc/) — needs the network. |

Shared chrome lives in `rnb-site.css` + `rnb-site.js`: the top cross-link bar and the
light / dark / night theme, remembered across all four pages in `localStorage`.

Publish by pushing this folder and pointing GitHub Pages at it; `index.html` is the landing page.

Originals before the restyle are in `.bak-pretheme/`.
