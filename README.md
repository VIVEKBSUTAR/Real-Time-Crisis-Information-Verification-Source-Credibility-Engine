# Sentinel Protocol

AI-powered crisis claim verification system with evidence ranking, image enhancement for OCR, and source credibility graphing.

## 1. What this project does

Sentinel Protocol verifies a text claim (or an uploaded image containing text) and returns:

1. Verdict (`TRUE`, `FALSE`, `UNVERIFIED`)
2. Confidence score
3. Evidence snippets with semantic similarity and relation (`supports` / `contradicts`)
4. Evidence summary + explanation text
5. Dynamic source credibility graph (trust and influence per source)

## 2. Current architecture (live path)

The default runtime is:

`backend/run_server.py` -> `app/server_lightweight.py`

Pipeline used by `/analyze_claim`:

1. Input text and/or image
2. Image Enhancement Agent (if image is provided and OCR path is used)
3. OCR extraction (best-of baseline/enhanced OCR path)
4. Semantic retrieval (Top-K)
5. NLI evaluation
6. Evidence Selection Agent (filters low-value evidence)
7. Stable post-NLI aggregation for verdict/confidence
8. Explainability generation
9. Source trust graph update and response payload

## 3. Repository layout

```text
demo1/
├── backend/
│   ├── app/
│   │   ├── server_lightweight.py           # Active backend server for demo
│   │   ├── dataset_loader.py               # Excel dataset ingestion
│   │   ├── core/
│   │   │   ├── semantic_pipeline.py
│   │   │   └── advanced_pipeline.py
│   │   ├── services/
│   │   │   ├── evidence_selection_agent.py
│   │   │   ├── image_enhancement_agent.py
│   │   │   ├── nli_service.py
│   │   │   ├── post_nli_service.py
│   │   │   ├── source_credibility_graph.py
│   │   │   └── ocr_service.py
│   │   └── explainability.py
│   ├── requirements.txt
│   └── run_server.py
├── frontend/
│   ├── src/
│   │   ├── MainLayout.jsx
│   │   └── pages/
│   │       ├── Intelligence.jsx
│   │       └── Analytics.jsx
│   └── package.json
├── QUICKSTART.md
└── SYSTEM_STATUS.md
```

## 4. Features implemented

### 4.1 Claim verification
- Semantic retrieval using sentence embeddings (`all-MiniLM-L6-v2` path in core pipeline)
- NLI relation classification (`supports`, `contradicts`, `neutral`)
- Final verdict + confidence with stable aggregation

### 4.2 Evidence Selection Agent
Implemented in `backend/app/services/evidence_selection_agent.py`

- Score function:
  `score = (w1 * similarity) + (w2 * relation_weight)`
- Relation weights:
  - `supports`: `1.0`
  - `contradicts`: `1.0`
  - `neutral`: `0.2`
- Rules:
  - filter out evidence with similarity `< 0.5`
  - down-rank neutral evidence
  - enforce support/contradict diversity where possible
  - dynamic per-request weighting (`w1`, `w2`) bounded for stability
  - deterministic tie-breaking

### 4.3 Image Enhancement Agent (new)
Implemented in `backend/app/services/image_enhancement_agent.py`

- Adaptive image enhancement before OCR:
  - deskew (rotation correction)
  - local contrast enhancement (CLAHE)
  - denoising
  - blur-aware sharpening
  - dark-image gamma lift
- Designed as deterministic pre-OCR processing (no side effects).

### 4.4 OCR extraction
Implemented in `backend/app/services/ocr_service.py`

- Preprocessing: grayscale -> denoise -> adaptive threshold -> morphology
- Two OCR paths are evaluated:
  1. baseline preprocessing
  2. enhanced-image preprocessing via Image Enhancement Agent
- Best text is selected with a deterministic OCR quality score
- OCR via `pytesseract`
- Output normalization for clean text
- API endpoint: `POST /extract_text_image`
- Also integrated into `POST /analyze_claim` when only image is provided

### 4.5 Dynamic Source Credibility Graph
Implemented in `backend/app/services/source_credibility_graph.py`

- Source nodes with trust score `[0.0, 1.0]`
- Simplified Bayesian-style trust updates
- Optional influence (`eigenvector_centrality`)
- Low credibility flag if trust `< 0.3`
- Returned in response as `source_credibility_graph` (`nodes`, `edges`, `source_evidence`)

### 4.6 Frontend graph + OCR UI
Implemented in `frontend/src/pages/Intelligence.jsx`

- Claim text submission
- Image upload button
- OCR text display in result panel
- Collapsible React Flow graph
- Clickable nodes with source-linked evidence
- Trust color coding:
  - Green: `trust > 0.7`
  - Yellow: `0.4 <= trust <= 0.7`
  - Red: `trust < 0.4`

## 5. Prerequisites

## 5.1 System requirements
- macOS/Linux/Windows
- Python 3.11 recommended
- Node.js 18+ and npm
- Git

## 5.2 Tesseract (required for OCR)

### macOS (Homebrew)
```bash
brew install tesseract
tesseract --version
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
tesseract --version
```

## 6. Setup and run (recommended)

## 6.1 Backend setup

```bash
cd backend
python3.11 -m venv .venv311
source .venv311/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Install ML/runtime packages required by semantic + NLI pipeline:

```bash
pip install sentence-transformers transformers torch pandas openpyxl scipy
```

Start backend:

```bash
python run_server.py
```

Backend runs on:
- `http://localhost:8000`

## 6.2 Frontend setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on:
- `http://localhost:3000`

## 6.3 Verify services quickly

```bash
curl http://localhost:8000/health
curl http://localhost:8000/analytics
```

## 7. Dataset requirements

Current dataset loader default path is hardcoded in:

`backend/app/dataset_loader.py`

Default expected file:

`/Volumes/V_Mac_SSD/Hackathon/Breaking Enigma/bharatfakenewskosh (3).xlsx`

If your file is elsewhere, either:

1. move/copy dataset to that path, or
2. edit `excel_path` in `DatasetLoader.__init__`.

## 8. API contract (active server)

## 8.1 GET `/health`
Returns backend status, readiness flags, and exposed endpoints.

## 8.2 GET `/analytics`
Returns aggregate dataset metrics used by Analytics page.

## 8.3 POST `/extract_text_image`
Request:

```json
{
  "image_base64": "data:image/png;base64,...."
}
```

Response:

```json
{
  "text": "clean extracted text"
}
```

## 8.4 POST `/analyze_claim`
Request:

```json
{
  "text": "Bridge collapsed in Pune",
  "image_base64": "optional base64 image string"
}
```

Response (shape):

```json
{
  "verdict": "TRUE | FALSE | UNVERIFIED",
  "confidence": 0.0,
  "explanation": "...",
  "evidence_summary": "...",
  "sources": [
    {
      "text": "...",
      "similarity": 0.82,
      "label": "TRUE",
      "relation": "supports",
      "score": 0.89,
      "source": "Reuters"
    }
  ],
  "claim": "...",
  "extracted_text": "...",
  "source_credibility_graph": {
    "nodes": [],
    "edges": [],
    "source_evidence": {}
  }
}
```

## 8.5 Legacy endpoints still available
These backend endpoints still exist even though they are removed from main frontend navigation:

- `GET /archived`
- `GET /threats`
- `GET /regions`

## 9. Frontend behavior

Main navigation currently includes:

- `Intelligence`
- `Analytics`

Intelligence page supports:

1. direct text claim verification
2. image upload + OCR-assisted verification
3. image enhancement + OCR extraction flow (image-only input path)
4. evidence panel
5. collapsible source graph with node inspection

## 10. Troubleshooting

## 10.1 `ModuleNotFoundError: sentence_transformers`
Install missing ML dependencies in the active backend venv:

```bash
pip install sentence-transformers transformers torch scipy pandas openpyxl
```

## 10.2 OCR errors (`pytesseract` / binary not found)

1. ensure Python package exists:
```bash
pip install pytesseract opencv-python Pillow
```
2. ensure system binary exists:
```bash
tesseract --version
```

Note: in `/analyze_claim`, OCR path is used when claim text is empty and `image_base64` is provided.

## 10.3 Same output for different claims

Check:

1. backend process is the latest one (`python run_server.py`)
2. no stale process is occupying port 8000
3. dataset is loading successfully from expected path
4. `sentence-transformers` and `transformers` are installed in current venv

## 10.4 Port already in use

Find and stop process:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
kill <PID>
```

## 11. Development notes

- `run_server.py` uses lightweight HTTP server path designed for fast demo iteration.
- `backend/app/main.py` exists as a FastAPI app scaffold and can be run separately via:

```bash
cd backend
source .venv311/bin/activate
uvicorn app.main:app --reload --port 8000
```

This scaffold mode exposes different response schemas than the lightweight demo server.

## 12. Security and operations

- Do not commit secrets/API keys.
- Keep heavy ML dependencies pinned in your environment.
- For stable demos, start backend first and wait for dataset/model initialization logs before first request.

## 13. Recommended demo flow

1. Start backend (`python run_server.py`)
2. Start frontend (`npm start`)
3. Open `http://localhost:3000`
4. Run one text claim verification
5. Run one image claim verification
6. Expand source graph and click nodes to show linked evidence

---

Built for hackathon rapid verification workflows with explainable, evidence-first output.
