# BadiCharts Studio — Desktop (Python)

A desktop application for programming indicators and drawing tools and sending Telegram
signals. The chart and the editor are the same HTML web app (**BADI-CHARTS-V2 v2.17.1**
chart + the **Monaco** editor) running inside the app window through QtWebEngine —
not rebuilt in Python.

## Run
```bash
pip install PySide6 cryptography quickjs
python BadiChartsStudio.py
```

## The two files
`BadiChartsStudio.py` is the complete app (studio page + desktop app, all readable).
`BadiChartsStudio_readable.py` is **generated literally from it** with one difference only:
an explanatory banner after the coding line — automated checks prove both copies produce
the byte-identical page and engine. The chart library itself is not embedded in either
file: the page loads it **directly from the official CDN link** (owner request):
`https://cdn.jsdelivr.net/gh/salahbadi19/BADI-CHARTS-V2@v2.17.1/chart.js`.
Everything lives in one file: the UI, the engine, BADI encryption, and the indicator
folder sync.

## Features
- **Candle countdown**: the native counter of the BADI-CHARTS-V2 library (v2.17.1) next to
  the live candle — used exactly as shipped (no page-side override), toggleable from Settings.
- **BadiCharts folder on disk**: every indicator or tool the user creates is saved as a
  real file in `BadiCharts/Indicators` (indicators .js/.py) or `BadiCharts/Tools`
  (tools .js), loaded at app boot and when the editor opens. The user can drop files
  directly into these folders and the app recognizes and imports them automatically
  (the disk is the reference).
- **BADI encryption (BADI Secure Indicator Format) the MetaTrader way**: the encrypt
  button in the editor writes a **.badi file next to the original indicator file** in the
  same folder (like .mq5/.ex5), and the encrypted file appears in the editor list **next
  to the real indicator name** with a lock icon. The 256-bit key is **fused inside the
  app** (`BADI_MASTER_KEY_HEX`) — fixed for everyone so the indicator runs everywhere,
  never written to any file, never copied and never shown (no path exports it from the
  app). Decrypting a corrupt or modified file is refused with a clear message
  (AES-256-GCM + AAD).
- **The encrypted indicator runs internally only**: its code never opens in the editor,
  is never saved anywhere and is never shown to the user, and its card on the chart has
  no edit button — its signals work like any other indicator. Before running any
  encrypted indicator the app checks it twice: a **forbidden-pattern scanner** (network,
  storage, app files and internal parts — any attempt to touch them rejects the whole
  file) and then a **trial run inside an isolated QuickJS** sandbox with no files and no
  network — suitable for paid indicators.
- **Settings button (next to the language button)**: manage the strip currencies +
  **chart appearance** — change the chart background and the bullish/bearish candle,
  grid, axis text, crosshair and drawing-tool colors **with any color freely** (hex like
  #22E08A or rgba — no fixed lists), applied instantly and saved, with a reset-to-default
  button + a BADI section (key fingerprint + BadiCharts folder path) — clicking a color
  swatch opens a **free color picker dialog** (ColorDialog with the alpha channel).
- **The logo in one place only**: the full BadiCharts logo in the app top bar (clicking
  it returns to the chart page) + a BADI STUDIO v2.17.1 line under it + the app icon in
  the title bar and taskbar.
- **Splash screen = the same logo reveal animation**: the icon drawn stroke by stroke →
  pulse → letters rising → the shine → the CHARTING ENGINE line — on a black background
  (a click skips it).
- **Join-channel button**: @badicharts (t.me/badicharts) + a **Bot Telegram** button
  (kept as text) opening the bot page with a "back to chart" button.
- **Currency strip**: currency chips (merged flags + name + payout — **no delete icon**,
  adding and removing from the + list) — **a (+) button beside the two arrows, sized like
  the signals-card button**, with a searchable list — two arrows (‹ ›) — **a
  theme-adaptive mini scrollbar** spanning the full strip width — not every currency can
  be removed (at least one always stays). Clicking a currency in the list adds it to the
  strip AND opens its chart.
- **Signals panel left of the chart (hide/show from the bell, never auto-opened) with two
  tabs**: **Signals** (running now, before the duration ends) and **History** (finished
  with their result) — a counter per tab, always-black cards + a **direction strip on the
  edge** + a BUY/SELL badge (green #22E08A / red #FF4D5E) + the currency flag + duration,
  indicator and entry price + the WIN/LOSS result — clicking a card opens its currency
  chart — signal and result sounds (WebAudio) + a mute button.
- **Simple info bar under the chart**: status (live) + **timezone (UTC±…)** + clock +
  FPS + **the fixed user ID BADI-XXXX-XXXX-XXXX (click to copy)** — no currency name.
- **Live candles always animating**: the live feed starts directly at boot — no
  play/pause button, and the dark/light toggle lives only in the app top bar (no
  duplicated button on the web bar).
- **Market API for indicators**: a user-programmed indicator can read any pair info
  (`Indicators.market.info(name)` → {name, payout, open, otc}) — the payout and the
  market open/closed state (OTC and crypto always open, forex Sunday 22:00 → Friday
  22:00 UTC), plus `assets()` for every currency, `added()` for strip currencies and
  `current()` for the chart currency.
- **Signals scoped to currencies chosen by the developer**: the `scope` setting in the
  indicator: `added` (strip currencies only) or `high` (highest payout ≥ minPayout — they
  do not have to be added) or `all` (every currency) — without it the indicator runs on
  the chart currency.
- **The Telegram chat ID comes from the indicator itself**: `signal()` returns
  {dir, price, chats} — the signal and its result are sent straight to that chat — the
  bot page holds the bot token only (no chat-ID field and no user-written message
  template).
- **A clean thumbnail per indicator**: captured once on first run **after the indicator
  really draws itself on the chart** (watching the first successful render) at high
  1440px resolution — shown on the indicator card and enlarged on click.
- **One clean chart**: no splitting and no blue frame around the chart — every panel is
  fully independent (currency + timeframe + payout) and the editor runs indicators on it.
- **The chart color follows the app live**: chart background, candles, grid, axes and the
  Monaco theme follow the app theme (dark/light) via setTheme — user customizations
  always apply on top.
- **Editor**: Monaco with a text fallback — a 3-step new-file wizard (JS indicator /
  tool / Python indicator) — a ready-made indicator library — autosave into the
  BadiCharts folder — Python indicators run in the app engine and draw on the chart.
- **Telegram signals** styled like the signal card + a WIN/LOSS result message + a chart
  screenshot — the bot page holds the settings and the signals log with Sent/Failed
  filters.
- **Light and fast**: Monaco loads only on first editor open, the last candle is pushed
  every second, smart render rate (33ms interactive / 150ms idle).

## Screenshots (BADI_SHOTS mode)
`splash` logo screen · `window-dark` top bar: logo + language + settings + channel ·
`settings-pop` currencies + chart appearance (free colors + picker) + BADI + indicators
folder · `studio-dark` / `studio-light` the studio (chart + the two-tab signals panel on
the left + info bar) · `panels-hidden` panel hidden · `login` login screen ·
`indicators` / `signals` the indicators and Telegram pages.
