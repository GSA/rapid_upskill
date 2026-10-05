---
title: "Styling the site"
parent: "Contributing"
nav_order: 6
status: "draft"
last_reviewed: "2026-10-05"
---

# Styling the site

The look of this site comes from one small file of values, called a preset. You can change colors, fonts, corner shape and heading sizes without writing any CSS.

The default preset, `ndstudio`, is a flat, high-contrast style on a white page, with a dark theme. It is inspired by [the National Design Studio website](https://ndstudio.gov/). It borrows the design language only: color, spacing and type scale. It uses no logos, images or font files from that site.

## Make your own style

1. Copy `docs/_data/themes/ndstudio.yml` to `docs/_data/themes/<yourname>.yml`.
2. Edit the values under `tokens:`. Edit the colors under `dark:` too, if you want a dark theme. Colors are six-digit hex values such as `"#1a1a1a"`.
3. In `docs/_config.yml`, set `theme_preset: <yourname>`.
4. Run `python3 .github/scripts/check_theme.py`. It fails if a text color is hard to read.
5. Open a pull request.

Two presets ship with the site: `ndstudio` (the default) and `classic`, an approximation of the stock Just the Docs look. Set `theme_preset: classic` to go back.

## Light and dark

A small button at the top right of the side menu switches between the light and dark theme. It remembers the choice in that browser. Until someone clicks it, the site follows the setting of the device. A preset with no `dark:` block has no dark theme and no button.

## What each token controls

| Token | Controls |
|---|---|
| `surface` | Page and sidebar background |
| `surface-raised` | Code blocks, callouts, search box, table row hover |
| `ink`, `ink-soft`, `muted` | Main text, secondary text, captions and table headers |
| `axis`, `hairline`, `rule` | Input borders, thin dividers, strong dividers |
| `link`, `link-hover` | Links, and the primary button on hover |
| `focus`, `danger` | Keyboard focus outline, warnings |
| `radius` | Corner roundness (`0` is square) |
| `font-sans`, `font-mono` | Font stacks for text and code |
| `tracking-body`, `tracking-heading` | Letter spacing |
| `weight-body`, `weight-strong`, `leading-heading` | Font weights and heading line height |
| `hero-size`, `h1-size`, `h2-size`, `h3-size`, `site-title-size` | Type sizes |
| `seal-size` | Width of the emblem above the site title |

## Emblem and fonts

The emblem above the site title is `seal` in `docs/_config.yml`, a file under `docs/assets/`. Its description is `seal_alt`. Leave `seal` empty for none.

The National Design Studio site uses PP Neue Montreal, a licensed commercial font. This repository does not include it. The default preset lists it first, so a reader who has it installed sees it. Everyone else gets Helvetica Neue, Arial or the system font.

## Rules for contributors

- Do not write colors such as `#fff` or `rgb(...)` in `docs/_sass/custom/`. Use `var(--nd-<token>)`.
- If you need a new value, add a token to every preset. Add it to `dark:` as well if it is a color. Then add it to the table above.
- Keep text colors at WCAG AA contrast, 4.5 to 1. The script checks the pairs the site uses.
- Keep the stylesheet in plain, old-style SCSS. GitHub Pages compiles it with an old Sass. Do not use `@use`, `math.div`, or other newer features.
- Pin the theme version in `docs/_config.yml`. Change the tag on purpose, then check a few pages.
