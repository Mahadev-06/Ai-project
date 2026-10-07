# ClaimLens — AI-Based Misinformation Detection System

**AI-Based Misinformation Detection System Using Natural Language Processing, Information Retrieval and Source Credibility Analysis**

ClaimLens helps investigate factual claims in text or public articles. It extracts checkable statements, retrieves relevant evidence, compares each statement with that evidence using natural language inference, and explains source credibility signals.

> **This system assists evidence review. It can miss context, retrieve incomplete information, or make mistakes. Results are evidence-relative findings, not guarantees of universal truth.**

## Screenshots

*Coming after Phase 3*

## Prerequisites

- **Python 3.11** (3.10–3.12 also supported; 3.13 may lack prebuilt wheels)
- **Node.js 18+** and npm
- **Git**
- ~2GB disk for model weights (downloaded on first setup)

## Quick Start

### 1. Clone and enter the project

```bash
git clone <repository-url>
cd claimlens
```

### 2. Backend Setup

```powershell
# Windows PowerShell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m spacy download en_core_web_sm
python -c "from app.services.model_manager import ModelManager; m = ModelManager(); m.load_all()"
uvicorn app.main:app --reload --port 8000
```

```bash
# Linux / WSL
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m spacy download en_core_web_sm
python -c "from app.services.model_manager import ModelManager; m = ModelManager(); m.load_all()"
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 4. Docker Compose (Alternative)

```bash
docker-compose up --build
```

Open http://localhost:3000

## Demonstration Workflow

1. Open ClaimLens in your browser
2. Paste a claim: *"The Great Wall of China is visible from space with the naked eye."*
3. Select **Local corpus** mode (default, no API keys needed)
4. Click **Analyze**
5. Review the extracted claims, evidence, stance analysis, and source credibility
6. Try the example claims for supported, contradicted, and opinion scenarios

## Evidence Modes

| Mode | Requirements | Coverage |
|------|-------------|----------|
| **Local corpus** (default) | No API keys | ~30 curated documents on science, health, geography, history |
| **Live web** | Brave Search API key | Web search + fact-check databases |

## Configuration

Copy `.env.example` to `.env` and configure:

```
BRAVE_API_KEY=         # Optional: enables live web search
GOOGLE_FACTCHECK_KEY=  # Optional: enables fact-check lookup
```

See `.env.example` for all settings.

## Project Structure

```
├── backend/          # Python FastAPI application
│   ├── app/          # Application code
│   ├── data/corpus/  # Evidence corpus
│   └── tests/        # Backend tests
├── frontend/         # React + TypeScript + Vite
│   ├── src/          # Application source
│   └── e2e/          # Playwright E2E tests
├── docs/             # Academic documentation
├── scripts/          # Setup and utility scripts
└── docker-compose.yml
```

## Academic Documentation

- [Architecture](docs/architecture.md)
- [Methodology](docs/methodology.md)
- [Evaluation](docs/evaluation.md)
- [Model & Data Card](docs/model-and-data-card.md)
- [API Reference](docs/api.md)
- [Demo & Viva Guide](docs/demo-and-viva.md)
- [Test Report](docs/test-report.md)
- [Implementation Status](docs/implementation-status.md)

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | React, TypeScript, Vite, Tailwind CSS | User interface |
| Backend | Python, FastAPI, Pydantic | API and orchestration |
| NLP | spaCy (en_core_web_sm) | Sentence segmentation, NER |
| Retrieval | BM25 + Sentence Transformers (all-MiniLM-L6-v2) | Evidence retrieval |
| Stance | Cross-encoder (nli-deberta-v3-small) | Natural language inference |
| Storage | SQLite | Job and report persistence |

All pretrained models are used as-is; they were not trained from scratch by this project.

## Deployment

### 1. Frontend on Vercel
The frontend is pre-configured for Vercel with SPA routing rewrites:
1. Go to [Vercel](https://vercel.com) and click **Add New Project**.
2. Import the `Mahadev-06/Ai-project` repository.
3. Configuration:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` (or leave as `./` — root `vercel.json` is included)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. In **Environment Variables**, add:
   - `VITE_API_URL`: Your deployed backend URL (e.g. `https://your-backend.onrender.com/api/v1`)
5. Click **Deploy**.

### 2. Backend on Cloud (Render / Railway / Fly.io / Docker)
The backend uses PyTorch, Sentence-Transformers, and DeBERTa models:
- **Docker**: Run `docker compose up -d` or deploy `backend/Dockerfile` to any container host.
- **Render / Railway / Fly.io**: Create a Web Service pointing to `backend/`, with start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## License

Academic project — see individual model licenses in [docs/model-and-data-card.md](docs/model-and-data-card.md).
