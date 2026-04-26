# @vyntia/design-tokens

Source of truth for VYNTIA brand tokens — colors, typography, spacing, layout.

Consumed by `apps/web` via npm workspaces. Editing `tokens.json` propagates to consumers; CSS variables in `apps/web/src/styles/tokens.css` are kept in sync manually for now.

## Usage

```js
const tokens = require('@vyntia/design-tokens');
console.log(tokens.color.primary); // "#6C63FF"
```

## Source

Brand kit: `vyntia_brand_ui.md`, `vyntia_full_system.md` (originally in `C:/Users/zeeke/Downloads/`).
