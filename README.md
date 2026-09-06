# Kifayat AI

```text
		██╗  ██╗██╗███████╗ █████╗ ██╗   ██╗ █████╗ ████████╗
		██║ ██╔╝██║██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝
		█████╔╝ ██║█████╗  ███████║ ╚████╔╝ ███████║   ██║
		██╔═██╗ ██║██╔══╝  ██╔══██║  ╚██╔╝  ██╔══██║   ██║
		██║  ██╗██║██║     ██║  ██║   ██║   ██║  ██║   ██║
		╚═╝  ╚═╝╚═╝╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝
        A Karachi Kitchen-Budget Price Companion, in Roman Urdu
```

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Storage-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Vanilla JS](https://img.shields.io/badge/Frontend-Vanilla%20JS-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![PBS Data](https://img.shields.io/badge/Data-PBS%20Weekly%20SPI-2E8B57?style=flat-square)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-000000?style=flat-square&logo=vercel&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square&logo=opensourceinitiative&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active%20Development-blue?style=flat-square)

---

## 🍲 What is Kifayat AI?

Kifayat AI is a **price-shock warning and purchase-timing companion** for Karachi's home-chefs, small bakeries, and micro food vendors — the people who run on thin margins and get hit hardest by sudden essential-commodity price swings, and who don't have time to read a government spreadsheet every Friday.

Today, a small *dhaba* operator or home-chef finds out flour or cooking oil got more expensive the same week they run out of stock — after the damage to their margin is already done. Kifayat AI moves that discovery earlier: it pulls Karachi's own price data directly from Pakistan's official weekly government release, tracks short-term volatility on the specific staples that matter most to a small kitchen operation, and lets a user ask — in plain Roman Urdu — whether a staple is about to get more expensive or cheaper, and get a direct, actionable answer back.

**Built for:** the Financial Inclusion track, Karachi region, AI Hackathon Pakistan.
**Core goal:** turn a 51-item, 17-city government spreadsheet nobody reads into one honest sentence a small vendor can act on before Friday's prices move again.

---

## 🌐 Application Details

| Attribute | Details |
|---|---|
| **Platform** | Web (desktop or mobile browser) |
| **Frontend** | HTML / CSS / vanilla JavaScript — no build step, no framework |
| **Backend Framework** | FastAPI (Python 3.12) |
| **Database** | SQLite (local dev/demo) |
| **Data Source** | Pakistan Bureau of Statistics — Weekly Sensitive Price Indicator (SPI) |
| **Scheduling** | APScheduler, in-process weekly refresh job |
| **NLU** | Rule-based Roman Urdu / English keyword matcher — no external LLM call required |

---

## ✨ Feature List

### 📊 Karachi Price Dashboard
- Tracks **13 kitchen staples** relevant to a small food business: wheat flour, sugar, cooking oil, vegetable ghee, three pulse varieties, two rice varieties, fresh milk, LPG cylinder, onions, and tomatoes.
- Every tracked item shows current price, 1-week % change, a trend direction, and a rolling volatility score, computed from real historical PBS data — not placeholder numbers.
- A small inline sparkline per item, hand-rolled in SVG, so the trend is visible at a glance without a charting library.

### 💬 Roman Urdu Query Chat
- Users ask in natural mixed Roman Urdu/English — e.g. *"oil sasta hoga ya mehanga?"* or *"chawal ka rate?"* — and get back a direct verdict plus the numbers behind it, never a bare recommendation with nothing to check it against.
- The matcher is a transparent keyword-alias dictionary (`app/nlu/roman_urdu.py`), deliberately **not** an LLM call — every answer is arithmetic over real government data, not a generated guess, which matters for a pitch that's explicitly scoped away from "AI oracle" claims.
- Unmatched queries get an honest fallback listing exactly which staples are supported, instead of a confident-sounding wrong guess.

### 🔁 Three-Layer Data Reliability
1. **Live fetch** — on startup (local) or every cold start (Vercel), the backend scrapes the PBS release page and downloads the latest Annexure Excel file directly. On Vercel, this means data auto-updates each week when PBS publishes new prices.
2. **Local cache** — every successfully fetched week is saved to `backend/data/history/` (local) or `/tmp/history/` (Vercel) and reused if a later live fetch fails.
3. **Bundled fallback workbook** — a real, previously-downloaded PBS Annexure ships in the repo, so the app has genuine data to show even fully offline. On Vercel, 8 real historical weeks ship with the function in `api/data/history/` for genuine multi-week trend calculations.
- The API surfaces which layer served the current data (`"source": "live" | "fallback_cached" | "manual_upload"`) on every relevant response, and the frontend shows this plainly as a badge rather than pretending everything is always live.

### 🛠️ Manual Data Recovery Path
- `POST /api/admin/refresh` — triggers an on-demand live fetch attempt, independent of the weekly schedule.
- `POST /api/admin/upload` — accepts a manually supplied `.xlsx` (e.g. downloaded by hand if the live site is unreachable during a judging round), parsed through the exact same pipeline as the automated fetch.

---

## 🏗️ Architecture

```text
┌─────────────┐        ┌─────────────────────┐        ┌────────────┐
│  Frontend (SPA)  │─────▶│  FastAPI Backend           │─────▶│  SQLite DB     │
│  HTML/CSS/JS     │◀─────│  ingestion · volatility ·  │◀─────│  prices + meta │
│  no build step   │        │  Roman Urdu NLU · scheduler│         └────────────┘
└─────────────┘        └─────────────────────┘
                                       │
                                       ▼
                     Pakistan Bureau of Statistics
                     weekly SPI release page + Annexure [Excel]
                     (fetched live, with local-cache and
                      bundled-workbook fallback)
```

---

## 🛠️ Tech Stack

### Frontend

| Technology | Role |
|---|---|
| **HTML / CSS** | Single-page layout: chat view, dashboard grid, source-badge footer |
| **Vanilla JavaScript** | `fetch`-based API calls, DOM rendering, hand-rolled inline SVG sparklines — no dependency, no build step |

### Backend

| Technology | Role |
|---|---|
| **FastAPI** | Async Python web framework, all routes in `app/main.py` |
| **SQLAlchemy** | ORM over the `prices` and `dataset_meta` tables |
| **APScheduler** | In-process weekly cron trigger for the live-fetch job |
| **requests + BeautifulSoup4** | Discovers the current week's PBS release page and its Annexure Excel link |
| **pandas + openpyxl** | Parses the real PBS Annexure workbook into a normalized price table |

---

## ⚙️ How It Works

### 1. Data Discovery & Ingestion
The backend finds the current week's PBS SPI release page (PBS does not expose a stable "latest" API, so this is done by parsing the release-index page's HTML for the newest "week ended on" link), follows it, and locates the actual `Annexure [Excel]` download link on that page rather than assuming a fixed, guessable filename.

### 2. Spreadsheet Parsing
PBS's real Annexure workbook lays out its `Appendix-A` sheet as a series of repeated city blocks running down the sheet — Islamabad, Rawalpindi, Gujranwala, Sialkot, Lahore, Faisalabad, Sargodha, Multan, Bahawalpur, **Karachi**, Hyderabad, Sukkur, Larkana, Peshawar, and others, 17 cities in total, matching PBS's own published methodology. The parser (`app/ingestion/parse_excel.py`) walks the sheet looking for the literal `"Karachi"` block heading and reads that block's averaged price column, rather than assuming a fixed row/column position — this was checked directly against a real downloaded Annexure file, not assumed from documentation.

### 3. Volatility & Verdict Engine
For each of the 13 tracked staples, `app/analytics/volatility.py` computes:
- 1-week percentage change against real historical prices,
- a direction label (rising / falling / flat, from a half-window average comparison),
- a rolling volatility score (standard deviation of weekly % changes),
- and a plain verdict — *"Buy now"*, *"Wait"*, or *"Stable"* — always shown alongside the numbers that produced it, never as a bare claim.

### 4. Roman Urdu Query Handling
`app/nlu/roman_urdu.py` tokenizes an incoming query and matches it against a hand-maintained alias dictionary (e.g. `"tail"`, `"tel"`, `"oil"` → Cooking Oil). This is a deliberate design choice: the "AI" in this project is scoped to natural-language *understanding*, while every number in the response comes from the volatility engine above — an LLM is never asked to invent a price or a trend.

---

## 📁 Project Structure

```text
kifayat-ai/
├── api/                              Vercel serverless function entry point
│   ├── index.py                      Entry point: sets env, adds api/ to sys.path, seeds DB
│   ├── requirements.txt              Vercel-specific dependencies (includes httpx)
│   ├── app/                          Full app copy (deployed to Vercel)
│   │   ├── main.py                   FastAPI app, _init_db(), all routes
│   │   ├── config.py                 Paths, IS_VERCEL detection, PBS_SPI_URL
│   │   ├── models.py                 SQLAlchemy models: Price, DatasetMeta
│   │   ├── db.py                     In-memory SQLite with StaticPool (Vercel)
│   │   ├── ingestion/
│   │   │   ├── discover.py           Scrapes PBS site for annexure link, downloads to /tmp on Vercel
│   │   │   ├── parse_excel.py        Finds Karachi column dynamically, parses real PBS workbook
│   │   │   └── seed_fallback.py      Seeds DB from history files + bundled fallback workbook
│   │   ├── analytics/
│   │   │   └── volatility.py         % change, direction, volatility score, buy/wait verdict
│   │   └── nlu/
│   │       └── roman_urdu.py         Keyword/alias matcher for Roman Urdu + English queries
│   └── data/
│       ├── fallback_sample.xlsx      Bundled PBS Annexure (deployed with function)
│       └── history/                  8 real PBS weeks for genuine trend calculations
├── backend/                          Local dev copy (not deployed to Vercel)
│   ├── app/
│   │   ├── main.py                   FastAPI app, APScheduler weekly refresh
│   │   ├── config.py                 Target items, PBS URLs, city constant
│   │   ├── models.py                 SQLAlchemy models: Price, DatasetMeta
│   │   ├── db.py                     SQLite file-based engine
│   │   ├── ingestion/
│   │   │   ├── discover.py           Finds current week's PBS page + Annexure link
│   │   │   ├── parse_excel.py        Normalizes real PBS workbook into Karachi price rows
│   │   │   └── seed_fallback.py      Loads cached history + bundled fallback workbook
│   │   ├── analytics/
│   │   │   └── volatility.py         % change, trend, volatility score, buy/wait verdict
│   │   └── nlu/
│   │       └── roman_urdu.py         Keyword/alias matcher for Roman Urdu + English queries
│   ├── data/
│   │   ├── fallback_sample.xlsx      A real downloaded PBS Annexure
│   │   └── history/                  Weeks of real, previously-fetched PBS Annexures
│   ├── tests/
│   │   └── test_core.py              Parser + NLU regression tests (15 passing)
│   └── requirements.txt
├── frontend/
│   ├── index.html                    Single-page app: chat view + dashboard grid
│   ├── styles.css                    Responsive layout, dark mode, accessibility
│   └── app.js                        fetch-based API calls, SVG sparklines, DOM rendering
├── vercel.json                       Vercel config: outputDirectory, /api/* rewrites
├── requirements.txt                  Root dependencies
└── README.md
```

> **Note:** `backend/` and `api/` contain the same app code. `backend/` is the local dev copy; `api/` is the Vercel-deployed copy with Vercel-specific adaptations (in-memory SQLite, `/tmp` filesystem, `StaticPool`, `index.py` entry point).

---

## 🚀 Local Setup

### Prerequisites
- Python 3.12+

### Step 1 — Clone the repository
```bash
git clone https://github.com/<your-org>/kifayat-ai.git
cd kifayat-ai
```

### Step 2 — Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
The backend runs at `http://127.0.0.1:8000` by default. On first startup it attempts a live PBS fetch, and falls back to the bundled real historical data if PBS is unreachable — check `GET /api/meta` to see which source actually served the current data.

### Step 3 — Frontend
Open `frontend/index.html` directly in a browser, or serve the folder with any static server. `frontend/app.js` talks to the backend at `http://127.0.0.1:8000/api` by default.

### Step 4 — Tests
```bash
cd backend
python -m pip install pytest
python -m pytest tests/test_core.py -v
```

---

## 📡 API Reference

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Liveness check |
| `/api/meta` | GET | Current data source (`live` / `fallback_cached` / `manual_upload`) and week-ending date |
| `/api/items` | GET | All 13 tracked staples with current price, trend, verdict, and history |
| `/api/items/{item_name}/history` | GET | Weekly price series for a single item |
| `/api/suggested` | GET | Top 3 items with actual price movement, for chat example chips |
| `/api/query` | POST | Roman Urdu / English natural-language query → matched items + verdicts |
| `/api/admin/refresh` | POST | Manually trigger a live PBS fetch attempt |
| `/api/admin/upload` | POST | Manually supply a `.xlsx` Annexure if PBS is unreachable |

---

## 🔍 Data Source Verification

Specific, checkable facts about the underlying dataset — verified directly against real downloaded PBS files, not taken on faith from documentation:

- PBS's Weekly Sensitive Price Indicator (SPI) covers **51 essential items across 50 markets in 17 cities nationally** — a national indicator, confirmed from PBS's own Price Statistics page.
- Karachi is **one averaged price column** within that national dataset (city block `"Karachi (10)"` in the real Annexure layout), not a separately-reported multi-market breakdown inside the spreadsheet — the parser extracts this single averaged column per item.
- All weeks of history bundled in `backend/data/history/` were confirmed, by direct inspection, to be genuine PBS Annexure files that parse into real Karachi prices for all 13 target items — not synthetic or placeholder data.
- **Live data verified:** All 13 item prices from the live PBS fetch match the published `Annex_03.09.2026.xlsx` exactly (to the decimal).
- **Not independently verified to a precise figure:** any specific claim about the exact number of physical markets sampled within Karachi city (as opposed to the single averaged price PBS publishes for it). Avoid stating a specific market count as a hard fact without opening a fresh Annexure and checking PBS's current methodology note.

---

## 🩺 Current Status & Known Gaps

This section is kept current deliberately, matched against the actual code — not left as a static disclaimer.

**Verified working:**
- Real 8-week Karachi price history, parsed successfully from genuine PBS Annexure files across every bundled week.
- Three-layer fallback (live → cache → bundled workbook) confirmed to work with no network access to PBS.
- Roman Urdu query matching and the full `/api/query` → chat UI path confirmed end-to-end.
- Test suite (`test_core.py`) passes — 15 tests covering parser, NLU, and all API endpoints.
- Dynamic example chips auto-select items with actual price movement for demo impact.
- `direction` (half-window average comparison) is the single trend measure shown — `pct_change_4w` removed to prevent contradictory readings.
- Synthetic data fabrication removed from `seed_fallback.py` — if data is missing, the app fails loudly instead of inventing prices.
- `pytest` and `httpx` included in `requirements.txt` — full dev setup from a single install command.

**Deployment status:**
- **Vercel:** Frontend served as static files, API as a Python serverless function with in-memory SQLite. Data auto-updates on every cold start — fetches the latest PBS annexure directly from pbs.gov.pk. Deploy with `vercel --prod`.
- **Local:** SQLite file + in-process APScheduler for weekly refresh.

---

## 🌐 Deploy to Vercel

```bash
npm i -g vercel
vercel login
vercel --prod
```

Vercel serves the frontend as static files and the API as a Python serverless function. The database is in-memory — on each cold start, the app first seeds from the bundled fallback (instant), then fetches the latest PBS data live from pbs.gov.pk. PBS publishes weekly SPI every Friday, so the next cold start after a new release automatically picks up the new week's prices.

**Vercel limitations:** Ephemeral filesystem (no SQLite persistence), no background scheduler (use Vercel Cron or external cron hitting `/api/admin/refresh`), manual upload disabled (use `/api/admin/refresh` instead).

- An early version of the ingestion pitch assumed Karachi was broken out as **13 separately-reported markets** inside the PBS spreadsheet. Direct inspection of a real downloaded Annexure file corrected this: Karachi is one averaged price column among 17 national cities, not a multi-row breakdown — the pitch language and the code were both aligned to the verified structure rather than the earlier assumption.
- A first-pass scan for "Karachi" inside the bundled history files initially came back empty and looked like a serious data-integrity problem. It wasn't — the scan only checked the first few rows of each sheet, and PBS's real layout places the Karachi city block roughly 60 rows down the sheet (after several other cities' blocks). Re-running the actual parser against the full file confirmed the data was there and correct all along. Documented here as a reminder to run the real parsing code against real files before concluding data is missing, rather than trusting a shallow manual scan.

---

## 📄 License

This project is open-source and available for educational and commercial use under the MIT License.

---

**Made with ❤️ by [Abdul Hayy Khan](https://www.linkedin.com/in/abdulhayykhan/)**