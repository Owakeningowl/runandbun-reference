# Run and Bun — Reference Site

Four pages, one theme, cross-linked.

| Page | File | What it is |
|---|---|---|
| AI Reference | `index.html` | Croven's RnB AI doc. Self-contained. |
| Trainer Sheet | `trainers.html` | All 436 trainers / 1,832 Pokémon, in the split-doc layout. |
| Dex | `dex.html` | Live embed of [may8th1995's RBDex](https://may8th1995.github.io/RBDex/). |
| Calc | `calc.html` | Live embed of [dekzeh's calculator](https://dekzeh.github.io/calc/). |

The dex and calc are embeds of the originals rather than copies, so they stay current
and the credit stays where it belongs.

## Shared chrome

`rnb-site.css` + `rnb-site.js` carry the top cross-link bar and the light / dark / night
theme, remembered across all four pages in `localStorage`.

## Trainer sheet data

`trainers.html` is generated from `rnb_trainers.json`:

```bash
python3 build_rnb_doc2.py
```

Teams only — no EVs, no computed stats, no AI commentary. Types and move typings come
from standard Gen 1–9 data; move power is the standard value, which RnB retunes for a
few moves.

## Publishing

GitHub Pages serves this folder from `main`; `index.html` is the landing page.
