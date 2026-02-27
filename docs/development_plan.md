# 🕸️ Website Data Extraction Tool — Development Plan

## 📌 What Is This Project?

A **Python-powered web scraping pipeline** that:
1. Accepts any website URL
2. Intelligently crawls it (static + JS-rendered)
3. Extracts structured business data (name, logo, services, contacts, branding, etc.)
4. Cleans & enriches data using an AI layer (Gemini/OpenAI)
5. Stores results in a database (MongoDB or PostgreSQL)
6. Outputs **rebuild-ready** structured profiles for website regeneration workflows

**Primary Use Case:** Feed this tool a client's existing website URL → get a fully structured brand + content profile → use it to rebuild/redesign the site automatically.

---

## 🛠️ Recommended Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.11+ | Fast iteration, rich scraping ecosystem |
| Static Scraping | `requests` + `BeautifulSoup4` | Simple, fast, battle-tested |
| Dynamic Scraping | `playwright` (async) | Best for React/Vue/Angular SPAs |
| AI Layer | `google-generativeai` (Gemini) or `openai` | LLM for cleaning/classifying text |
| Data Validation | `pydantic` | Strict schema enforcement |
| Database | **MongoDB** via `pymongo` or `motor` (async) | Perfect for flexible JSON profiles |
| API Layer | `FastAPI` | Async, fast, auto-docs |
| Task Queue | `celery` + `redis` (Phase 5 only) | Background scraping jobs |
| CSS Analysis | `tinycss2` or `cssutils` | Parse stylesheets for branding |
| Color Extraction | `colorthief` + `Pillow` | Extract dominant colors from logo/images |
| Config | `python-dotenv` | Manage API keys and DB URIs |
| Logging | `loguru` | Structured, readable logs |

---

## 📁 Recommended Folder Structure

```
d:\scraper\
├── docs\
│   ├── plan.txt
│   └── development_plan.md       ← This file
├── app\
│   ├── __init__.py
│   ├── main.py                   ← FastAPI app entry point
│   ├── config.py                 ← Settings from .env
│   │
│   ├── modules\
│   │   ├── __init__.py
│   │   ├── validator.py          ← Module 1: URL validation
│   │   ├── crawler.py            ← Module 2: Static + Dynamic crawler
│   │   ├── parser.py             ← Module 3: HTML parsing engine
│   │   ├── branding.py           ← Module 4: Color/font/theme extractor
│   │   ├── ai_processor.py       ← Module 5: AI cleaning & classification
│   │   └── normalizer.py         ← Module 6: Data normalization
│   │
│   ├── models\
│   │   ├── __init__.py
│   │   └── profile.py            ← Pydantic models (data schema)
│   │
│   ├── database\
│   │   ├── __init__.py
│   │   └── mongo.py              ← Module 7: MongoDB operations
│   │
│   └── api\
│       ├── __init__.py
│       └── routes.py             ← REST API endpoints
│
├── .env                          ← API keys, DB URI (never commit)
├── .env.example                  ← Template for .env
├── requirements.txt
└── README.md
```

---

## 🗺️ Development Roadmap (Phases)

---

### ✅ Phase 1 — Project Setup + MVP Core (Day 1–2)

**Goal:** Working end-to-end pipeline for static websites.

#### Tasks:
1. Init project structure — create all folders and `__init__.py` files
2. `requirements.txt` — pin all dependencies
3. `config.py` — load `.env` vars (DB URI, AI key)
4. `models/profile.py` — define the master Pydantic schema
5. `modules/validator.py` — URL normalization, `robots.txt` check, reachability
6. `modules/crawler.py` (Mode A) — requests + retry + rate limiting
7. `modules/parser.py` — BeautifulSoup extraction (name, email, phone, about, services, social links, favicon)
8. `database/mongo.py` — connect, insert, upsert by URL
9. `main.py` (script mode) — wire all modules together for CLI testing

**Deliverable:** Run `python -m app.main https://example.com` → structured JSON stored in MongoDB.

---

### ✅ Phase 2 — Dynamic Website Support (Day 2–3)

**Goal:** Handle JS-rendered SPAs (React/Vue/Next.js sites).

#### Tasks:
1. `modules/crawler.py` (Mode B) — add `playwright` async crawler
2. Auto-detect if a page is static or dynamic (check for JS frameworks in HTML)
3. Crawl sub-pages: `/about`, `/contact`, `/services` automatically
4. Handle timeouts, redirects, 404s gracefully

**Deliverable:** Same pipeline working on dynamic websites like Next.js/React.

---

### ✅ Phase 3 — AI Intelligence Layer (Day 3–4)

**Goal:** Clean, classify, and summarize raw scraped text with LLM.

#### Tasks:
1. `modules/ai_processor.py`:
   - Clean and deduplicate scraped text
   - Summarize "About" section into 2–3 sentences
   - Classify business type (Restaurant / Clinic / SaaS / E-commerce / Portfolio etc.)
   - Extract clean services list from messy text
   - Standardize contact formats (phone, email, address)
   - Improve grammar of extracted paragraphs
2. Use **prompt chaining** — separate prompts for each task (more reliable than one giant prompt)
3. Add response validation via Pydantic to catch LLM hallucinations

**Deliverable:** Raw messy scrape → clean, AI-enriched structured profile.

---

### ✅ Phase 4 — Branding Intelligence (Day 4–5)

**Goal:** Extract visual identity for design rebuilding.

#### Tasks:
1. `modules/branding.py`:
   - Parse CSS files linked in `<head>` → extract font-families, CSS variables
   - Detect primary/secondary/accent colors from CSS `color` and `background-color`
   - Download logo image → use `colorthief` to extract dominant color palette
   - Detect design style heuristics (e.g., many gradients = modern, serif fonts = corporate)
   - Extract button styles (border-radius, shadows)
2. Store full `branding` object in the profile schema

**Deliverable:** A brand profile object with colors, fonts, and layout style classifier.

---

### ✅ Phase 5 — API + Production Readiness (Day 5–7)

**Goal:** Wrap everything in a FastAPI REST API; make it production-grade.

#### Tasks:
1. `api/routes.py` — `POST /scrape` endpoint, `GET /profile/{url}` endpoint
2. `main.py` — launch FastAPI app
3. Add background task processing (FastAPI `BackgroundTasks` → upgrade to Celery/Redis later)
4. Add Loguru logging throughout all modules
5. Error handling: HTTP error codes, scraping failures, AI API failures
6. Add rate limiting on the API
7. Add version history in DB (re-scrape tracking)
8. Write `README.md`

**Deliverable:** Fully operational REST API with `POST /scrape` endpoint.

---

## 📐 Master Data Schema (Reference)

```json
{
  "source_url": "https://example.com",
  "scraped_at": "2026-02-26T12:00:00Z",
  "crawl_status": "success",
  "confidence_score": 0.87,

  "business_profile": {
    "name": "Example Corp",
    "industry": "SaaS",
    "business_type": "B2B Software",
    "about": "A concise 2-3 sentence AI summary.",
    "services": ["Service A", "Service B"],
    "keywords": ["keyword1", "keyword2"]
  },

  "contact": {
    "email": ["hello@example.com"],
    "phone": ["+1-800-000-0000"],
    "address": "123 Main St, City, Country",
    "social_links": {
      "twitter": "https://twitter.com/example",
      "linkedin": "https://linkedin.com/company/example"
    }
  },

  "branding": {
    "logo_url": "https://example.com/logo.png",
    "favicon_url": "https://example.com/favicon.ico",
    "primary_color": "#2D6FE8",
    "color_palette": ["#2D6FE8", "#FFFFFF", "#1A1A2E"],
    "fonts": ["Inter", "Roboto"],
    "layout_style": "modern-minimal",
    "button_style": { "border_radius": "8px", "style": "filled" }
  },

  "content_sections": {
    "homepage_heading": "Welcome to Example Corp",
    "about_raw": "Full raw about text...",
    "services_raw": ["Raw service text..."]
  },

  "technical_metadata": {
    "is_dynamic": true,
    "framework_detected": "React",
    "page_title": "Example Corp | Home",
    "meta_description": "We build great software.",
    "canonical_url": "https://example.com"
  }
}
```

---

## ⚡ Quick Start Commands (After Setup)

```powershell
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Copy and fill .env
copy .env.example .env

# 5. Run CLI test (Phase 1)
python -m app.main https://example.com

# 6. Run API server (Phase 5)
uvicorn app.main:app --reload
```

---

## 🔑 Key Implementation Tips

### Speed Tips
- **Start with static crawler** — `requests` is instant; covers 90% of sites first
- **Playwright only when needed** — detect JS frameworks before launching headless browser
- **Prompt chaining > one mega-prompt** — smaller focused LLM calls are faster, cheaper, and more reliable

### Quality Tips
- **Pydantic models everywhere** — catches bad data at module boundaries, not when writing to DB
- **Confidence score** — count how many fields were successfully extracted vs. expected; store as float 0–1
- **Store raw data too** — always save raw scraped text alongside processed results; lets you reprocess with better AI later without re-crawling

### Avoiding Problems
- Always check `robots.txt` before crawling (use `urllib.robotparser`)
- Set `User-Agent` to a realistic browser string to avoid blocks
- Add 1–2 second delay between page requests
- Handle encoding issues (`response.encoding = 'utf-8'`)

---

## 🏁 7-Day Build Order (Fastest Path to Working Tool)

| Day | Build Target | Deliverable |
|---|---|---|
| Day 1 | Setup + `validator.py` + `crawler.py` (static) + `parser.py` | CLI test works |
| Day 2 | `mongo.py` + `normalizer.py` + Pydantic schema | Full MVP end-to-end |
| Day 3 | `crawler.py` Mode B (Playwright) | SPAs supported |
| Day 4 | `ai_processor.py` | AI enrichment works |
| Day 5 | `branding.py` | Color + font extraction |
| Day 6 | `api/routes.py` | FastAPI REST API live |
| Day 7 | Logging, error handling, retry logic, README | Production-ready |

> **Tip:** Start with `python -m app.main` as a CLI script. Only wrap in FastAPI once the core pipeline is fully working. This keeps iteration fast.

> **Important:** Use **MongoDB** (not PostgreSQL) — the schema will evolve as you discover what different websites return. Flexible document storage is far more practical here.

> **Warning:** Don't start with Celery/Redis. Use FastAPI `BackgroundTasks` first. Add Celery only when you actually need job queuing at scale.

---

## 🔐 Legal & Ethical Safeguards

- Always respect `robots.txt`
- Implement crawl delay between requests
- Avoid scraping authenticated/protected pages
- Use AI rewriting to transform (not copy) content
- Store only publicly available data

---

*Plan created: 2026-02-26*
