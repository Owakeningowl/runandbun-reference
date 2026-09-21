# Run and Bun — Reference Site

Four pages, one theme, cross-linked.

| Page | File | What it is |
|---|---|---|
| AI Reference | `index.html` | Croven's RnB AI doc. Self-contained. |
| Trainer Sheet | `trainers.html` | All 436 trainers / 1,832 Pokémon as sprite cards, searchable. |
| Dex | `dex.html` | Live embed of [may8th1995's RBDex](https://may8th1995.github.io/RBDex/). |
| Calc | `calc.html` | Live embed of [dekzeh's calculator](https://dekzeh.github.io/calc/). |

The dex and calc are embeds of the originals rather than copies, so they stay current
and the credit stays where it belongs.

## Shared chrome

`rnb-site.css` + `rnb-site.js` carry the top cross-link bar and the light / dark / night
theme, remembered across all four pages in `localStorage`.

## Trainer sheet data

`rnb-data.js` is generated from `rnb_trainers.json`:

```bash
python3 build_rnb_sheet.py
```

Types and move typings are filled in from standard Gen 1–9 data. Base stats and move
power are deliberately left out — RnB retunes some of them, and this repo has no
verified source for its values.

## Publishing

GitHub Pages serves this folder from `main`; `index.html` is the landing page.
