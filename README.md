# ResellerOS

ResellerOS is an offline-first, privacy-preserving operating system for independent resellers. It combines inventory management, eBay listing prep, bookkeeping, trend research, and local-first AI assistants into a single open-source toolchain.

## Features

- **Inventory management** with full CRUD, tagging, attachments, and bulk support via CSV import/export.
- **Listings & lots** builder with AI-assisted SEO, pricing, and marketing copy powered by local LLMs (Ollama).
- **Accounting tools** for expenses, sales, and profit tracking with tax estimator inputs.
- **Research workspace** that keeps offline snapshots and produces AI-assisted summaries for sourcing decisions.
- **Admin console** for tax rules, integrations, theming, and data backup/restore.
- **Offline-first architecture** using SQLite with write-ahead logging, heuristic fallbacks when AI or network services are unavailable, and background jobs that log activity without requiring connectivity.

## Architecture

| Layer | Technology | Notes |
| ----- | ---------- | ----- |
| Frontend | React + Vite + Tailwind | Local SPA served via Vite dev server or static build |
| Backend | Node.js (Express) | REST API for all modules and AI orchestration |
| Database | SQLite | Portable database stored in `db/database.sqlite` |
| AI | Ollama (local) | Models like `mistral` or `llama3`. Falls back to heuristics when offline |
| Jobs | node-cron | Hourly placeholder sync demonstrating offline-safe background tasks |

```
reseller-os/
├── ai/                   # AI + NLP configuration
├── backend/              # Express API
├── db/                   # SQLite schema and data
├── frontend/             # React SPA
└── shared/               # Data accessible by both backend and offline research
```

## Getting Started

1. **Install dependencies**

   ```bash
   cd backend && npm install
   cd ../frontend && npm install
   ```

2. **Run backend**

   ```bash
   cd backend
   npm run start
   ```

   The API is available at `http://localhost:4000/health`.

3. **Run frontend**

   ```bash
   cd frontend
   npm run dev
   ```

   The web app runs at `http://localhost:5173` by default.

4. **(Optional) Enable local AI**

   Install [Ollama](https://ollama.ai/) and run:

   ```bash
   ollama pull mistral
   ollama serve
   ```

   The backend automatically connects to `http://127.0.0.1:11434` for AI features. When the service is unavailable, deterministic heuristics generate usable fallback copy.

## Data Portability

- All user data lives in the local SQLite database (`db/database.sqlite`).
- Backups can be created by copying the file or exporting JSON via the API endpoints.
- CSV import/export is implemented on the frontend and interacts with the REST API for ingestion.

## License

ResellerOS is released under the MIT License. All dependencies are permissive and open source.
