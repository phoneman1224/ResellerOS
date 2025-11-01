# 📦 ResellerOS

**An AI-Powered, Offline-First, Open Source Business Management Platform for Resellers**

---

## 🧭 Overview

**ResellerOS** is a self-hosted, offline-first, privacy-focused system designed to help independent resellers manage their entire resale business. This includes inventory tracking, listing generation, pricing research, expense tracking, profit analysis, tax estimation, and advanced market research — all enhanced with **locally running AI/LLM tools**.

> 🎯 Designed for resellers who want automation and business insights **without giving up control** to cloud-based or paid SaaS tools.

---

## 🚀 Key Features

### ✅ Local, Free & Open Source
- 100% self-hosted
- Runs on a local Linux PC (desktop or server)
- No subscriptions, no cloud lock-in
- All libraries and models are open-source

### 🧠 AI + Local LLM Integration
- **Runs local LLMs via [Ollama](https://ollama.com)** (e.g., Mistral, LLaMA, Gemma)
- SEO generator for eBay titles and descriptions
- Market/trend analyzer across eBay, Reddit, YouTube, TikTok, Amazon, Mercari
- Pricing assistant (based on sales data + AI insights)
- Tagging and category prediction
- Content generation (social media, bundles, descriptions)
- AI-powered business summaries and trend reports

### 📦 Inventory Management
- Add/edit/delete items with cost, quantity, condition, category
- Image attachments and tagging
- Aging alerts, inventory health indicators
- CSV import/export
- Fully editable and user-controlled

### 🧾 Sales, Expenses & Profit
- Track sales from eBay and other platforms
- Import sold item data via eBay API (no customer info)
- Calculate net/gross profit per item or lot
- Add and categorize business expenses (with deductible flag)
- Estimate taxable income and generate reports

### 📤 eBay Listing Builder (with Draft Push)
- Create draft listings (individual or lots)
- Push drafts to eBay via eBay Inventory API
- Auto-generate titles, descriptions, and prices using local AI
- Attach images and manage listing status
- SEO health check for drafts

### 📦 Lot Maker
- Combine multiple inventory items into a lot
- Auto-price based on item total
- Generate bundle listings with AI-enhanced titles and descriptions
- Full CRUD and history tracking for lot items

### 🔍 Market Research & Trends (AI-Powered)
- Scrape + summarize from:
  - eBay
  - Reddit (reseller subs)
  - YouTube (reseller content)
  - TikTok (hashtags/trends)
  - Amazon / Mercari (scraping)
- Local NLP and summarization using LLM
- Watchlists, price tracking, and alerts
- Trend detection and sourcing suggestions

### 📊 Tax Estimation & Reports
- Track income, expenses, and COGS
- Estimate quarterly self-employment tax
- Flag deductible expenses
- Export Schedule C-style CSV/PDF reports

### ⚙️ Admin Tools
- Theme customization (light/dark, fonts, UI)
- Manage dropdowns (platforms, sources, categories)
- Backup/restore local database
- Configure tax brackets, business rules, and API keys
- Toggle/enable/disable optional modules

---

## 🧱 Architecture

| Layer        | Stack / Tool                             |
|--------------|-------------------------------------------|
| **Frontend** | React + Vite + Tailwind CSS              |
| **Backend**  | Node.js + Express                        |
| **Database** | SQLite (.db file stored locally)         |
| **AI Engine**| Ollama (Mistral / LLaMA / Gemma)         |
| **NLP Tools**| spaCy, HuggingFace Transformers, fastText|
| **Scraping** | Puppeteer / Playwright / scrapy          |
| **Packaging**| Electron or Tauri (optional desktop app) |

---

## 🗂 Folder Structure (Scaffold)

reseller-os/ ├── backend/ │   ├── routes/ │   ├── controllers/ │   ├── services/       # eBay API, AI, scraping, etc. │   ├── models/ │   ├── jobs/ │   └── server.js ├── frontend/ │   └── src/ │       ├── components/ │       ├── pages/ │       ├── context/ │       └── App.jsx ├── ai/ │   ├── ollama/         # LLM configs │   ├── prompts/        # Custom prompt templates │   └── nlp/            # NLP scripts and processors ├── db/ │   ├── schema.sql │   └── database.sqlite ├── scripts/            # CLI tools, sync jobs, backup ├── shared/ ├── .env ├── README.md └── package.json

---

## ⚙️ Scaffold CLI Setup (Optional)

To auto-generate folders:

1. Create a file called `scaffold.js` and paste this:

```js
const fs = require('fs-extra');
const path = require('path');

const folders = [
  'backend/routes',
  'backend/controllers',
  'backend/services',
  'backend/models',
  'backend/jobs',
  'frontend/src/components',
  'frontend/src/pages',
  'frontend/src/context',
  'ai/ollama',
  'ai/prompts',
  'ai/nlp',
  'db',
  'scripts',
  'shared',
];

(async () => {
  for (const folder of folders) {
    await fs.ensureDir(path.join(__dirname, folder));
    console.log(`✔ Created: ${folder}`);
  }

  await fs.outputFile('db/schema.sql', '-- SQLite schema file');
  await fs.outputFile('.env', '# Environment variables go here');
  await fs.outputFile('README.md', '// See root for actual README');
  console.log('\n✅ Scaffold complete.');
})();

2. Run it:



npm install fs-extra
node scaffold.js


---

🤝 Contributing

Want to contribute? Fork the repo, make your changes, and submit a pull request. Please keep everything:

Open source

AI-powered

Local-first



---

📄 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute it for personal or commercial purposes.


---

🙏 Credits

ResellerOS was envisioned to help solo resellers run smarter businesses with zero cost, using modern AI responsibly and privately.

---

