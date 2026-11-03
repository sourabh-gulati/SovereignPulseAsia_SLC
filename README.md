# Sovereign Pulse Asia_SLC

Sovereign Pulse Asia_SLC is a fixed-income dashboard for comparing government-bond yield history across Asian markets. It currently covers India, Japan, and Taiwan, with a consistent interactive chart experience for each market.

## Capabilities

| Market | Maturities | History shown | Primary public source |
| --- | --- | --- | --- |
| India | 1Y, 2Y, 5Y, 10Y | Monthly month-end yields | Reserve Bank of India DBIE report 217 |
| Japan | 1Y, 2Y, 5Y, 10Y | Most recent 12 months of daily yields | [Japan Ministry of Finance JGB interest rates](https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/index.html) |
| Taiwan | 2Y, 5Y, 10Y | Recent daily benchmark yields | [Taipei Exchange government-bond information](https://www.tpex.org.tw/web/bond/gov_bond/market_data/gov_daily.php?l=zh-tw) |

The dashboard provides:

- A country selector to jump between markets, with country flags in market headings.
- Maturity selectors tailored to each market.
- Latest yield, observation date, and change over the displayed history.
- Interactive SVG charts: hover across a chart to see the nearest date and yield.
- Loading, no-data, and upstream-source error states.

## How data reaches the screen

```text
Official public market-data source
              |
              v
FastAPI service (validation, parsing, normalisation)
              |
              v
JSON endpoint under /api
              |
              v
Vue 3 dashboard (metric, chart, tooltip and source label)
```

The browser calls only the FastAPI API. It never connects directly to PostgreSQL or an external market-data provider.

### Data collection and normalisation

- **India:** the backend reads the public RBI DBIE report-217 data mirror and converts its financial-year/month layout into dated monthly month-end yield observations.
- **Japan:** the backend downloads the Ministry of Finance constant-maturity JGB CSV, validates the selected tenor, and retains the most recent year of usable daily observations.
- **Taiwan:** the backend reads the Taipei Exchange's daily `.xls` benchmark workbooks, extracts the published 2Y, 5Y, and 10Y weighted-average yields, and caches recent history for 12 hours.
- **US Treasury import support:** US Treasury observations can be imported separately into PostgreSQL/Supabase. This stored-data endpoint never downloads Treasury data during a browser page load.

Missing observations are omitted; no yield is replaced with zero or fabricated. All yield values are percentages.

Each country endpoint returns a common payload containing its source, selected tenor, data status, and ordered `{ date, yield_percent }` points. The shared shape lets the frontend reuse one chart component while retaining country-specific maturities and source wording.

### Rendering

The Vue 3 frontend uses TypeScript and Vite. `SovereignYieldChart.vue` fetches the selected endpoint with Axios, computes the SVG range and coordinates from the returned observations, and renders the yield line, gradient area, summary metric, source attribution, and hover tooltip. Country flags are local SVG assets, so the UI does not depend on third-party flag-image requests.

## Run locally with Docker

1. Create a Supabase project and copy its PostgreSQL session-pooler URL.
2. Copy `.env.example` to `.env` and set `DATABASE_URL`. Keep this file private.
3. Start the stack:

```bash
docker compose up --build
```

- UI: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Historical US Treasury import

```bash
cd backend
python scripts/import_treasury_history.py --month 202611
```

Use a historical `YYYYMM` month. Re-running an import updates matching date/tenor rows without duplicates. The stored-yield endpoint selects the newest observation dated yesterday or earlier, so it never displays an in-progress current-day value.

## API

- `GET /api/india-gsec/history?tenor=10Y` — valid tenors: `1Y`, `2Y`, `5Y`, `10Y`
- `GET /api/japan-gsec/history?tenor=10Y` — valid tenors: `1Y`, `2Y`, `5Y`, `10Y`
- `GET /api/taiwan-gsec/history?tenor=10Y` — valid tenors: `2Y`, `5Y`, `10Y`
- `GET /api/treasury-yields/latest` — latest eligible stored US Treasury data
- `GET /health`

## Development checks

```bash
cd backend
python -m pytest -q

cd ../frontend
npm run build
```

## Security

- Never commit `.env`, connection strings, API keys, or Supabase credentials.
- Keep `CORS_ORIGINS` explicit outside local development.
- Use a restricted database role and deployment-host secrets in production.

