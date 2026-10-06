---
name: bancolombia-visual-style
description: Visual foundations (tokens, palette, typography, accessibility, components) for the HTML presentation, the app mockup and the notebook charts. Load before writing any chart, HTML or CSS.
---

# Visual style (inspired by the Bancolombia design system principles)

Principles: foundations first (tokens before components), one naming scheme shared by design and code, atomic components with explicit states, light and dark mode, AAA-oriented accessibility, sober and clean layouts, human (non-banking) language.

## Color tokens
```css
--color-amarillo: #fdda24;  /* brand accent: highlights, active states, never text on white */
--color-verde:    #00c389;  /* positive / meets target */
--color-morado:   #9063cd;  /* secondary series, model / AI elements */
--color-naranja:  #ff7f41;  /* warning / below target */
--color-rosado:   #f5b6cd;  /* soft background accents */
--color-azul:     #59cbe8;  /* data / information series */
--color-negro:    #2a2625;  /* primary text, dark surfaces */
--color-blanco:   #ffffff;  /* light surfaces */
```
Derived neutrals (for text and borders): `--gris-700: #545050`, `--gris-400: #9e9a99`, `--gris-200: #e6e3e2`, `--gris-100: #f4f3f2`.

## Usage rules
- Text is always `--color-negro` on light or `--color-blanco` on dark. Brand colors are used for fills, marks and accents, not for body text.
- Yellow on white fails contrast: use yellow as a fill with black text on top.
- Status semantics are fixed: verde = cumple, naranja = alerta, gris = sin dato. Never encode status by color alone; add an icon or label.
- Categorical chart order: azul, morado, verde, naranja, rosado. Max 5 series; group the rest as "Otros".
- Dark mode: surfaces `--color-negro`, text `--color-blanco`, keep the same accents.

## Typography and spacing
- Font: system sans stack (`"Open Sans", "Segoe UI", system-ui, sans-serif`), sizes in rem: 0.875 / 1 / 1.25 / 1.75 / 2.5.
- Bold only for headings and key numbers. Avoid ALL CAPS except short labels.
- Spacing scale (rem): 0.25 / 0.5 / 1 / 1.5 / 2 / 3. Corner radius 12px for cards, 999px for pills.

## Presentation-specific
- Slides: one idea per slide, ≤ 25 words of body text, numbers bigger than words.
- Charts: direct labels instead of legends when possible, no 3D, no gridline clutter, start bars at zero.
