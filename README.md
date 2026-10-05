# LegalEase — AI-Powered Legal Document Generator

LegalEase is a Streamlit + FastAPI application for generating editable legal-document drafts with Google Gemini and exporting them as TXT, DOCX, or PDF.

> **Important:** LegalEase produces AI-assisted drafts and general information. It is not a substitute for advice from a qualified lawyer, and users should review documents for the applicable jurisdiction before signing or relying on them.

## Architecture

```text
Streamlit UI
    │
    ├── POST /generate ──────► FastAPI
    │                              │
    │                              └── GeminiDocumentGenerator
    │                                      │
    │                                      └── Google Gemini API
    │
    └── POST /export ─────────► FastAPI
                                   │
                                   ├── DOCX formatter
                                   ├── PDF formatter
                                   └── TXT formatter
```

The supplied project document specifies Streamlit + FastAPI + Gemini, editable preview, and TXT/DOCX/PDF export. This implementation keeps that architecture while using Google's current `google-genai` SDK rather than the older `google-generativeai` package.

## Project tree

```text
LegalEase/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── ai_core/
│   │   ├── __init__.py
│   │   └── gemini_generator.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── document_service.py
│   └── utils/
│       ├── __init__.py
│       ├── text_utils.py
│       └── formatters.py
├── frontend/
│   └── app.py
├── tests/
│   ├── __init__.py
│   ├── test_health.py
│   ├── test_generate.py
│   └── test_formatters.py
├── assets/
│   └── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── Procfile
├── Dockerfile
└── docker-compose.yml
```

## 1. Prerequisites

- Python 3.11 or newer
- A Google Gemini API key
- VS Code

## 2. Create and activate a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 4. Configure Gemini

Copy `.env.example` to `.env` and set:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
DEMO_MODE=false
BACKEND_URL=http://127.0.0.1:8000
```

`GEMINI_MODEL` is configurable. If a model is unavailable to your API account, change it to another currently available Gemini model.

For a completely local UI/API smoke test without a Gemini key:

```env
DEMO_MODE=true
```

Demo mode deliberately returns a clearly labelled sample draft instead of calling an LLM.

## 5. Run the backend

From the project root:

```bash
uvicorn backend.main:app --reload --port 8000
```

Open:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## 6. Run the frontend

Open a second terminal with the same virtual environment:

```bash
streamlit run frontend/app.py
```

Then open the URL Streamlit prints, normally:

```text
http://localhost:8501
```

## 7. Test

Run:

```bash
pytest -q
```

The tests do not require a Gemini API key because they use demo mode.

For an API smoke test:

```bash
curl http://127.0.0.1:8000/health
```

PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## 8. Using the application

1. Select or enter a document type.
2. Enter the parties.
3. Enter terms separated by semicolons.
4. Enter the effective date.
5. Optionally enter jurisdiction and additional instructions.
6. Optionally upload a logo.
7. Click **Generate Document**.
8. Review the generated draft.
9. Click **Edit Document** if you want to change the text.
10. Download TXT, DOCX, or PDF.

The frontend sends all generation data to FastAPI. It never exposes the Gemini API key to the browser/UI.

## 9. API examples

### Generate

```http
POST /generate
Content-Type: application/json
```

```json
{
  "document_type": "Non-Disclosure Agreement",
  "parties": "Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
  "terms": [
    "Confidential information must be protected",
    "Permitted purpose is evaluation of a proposed project",
    "Confidentiality period is 2 years"
  ],
  "effective_date": "September 24, 2026",
  "jurisdiction": "India",
  "additional_instructions": "Use clear section headings and plain but formal language."
}
```

### Export

```http
POST /export
Content-Type: application/json
```

```json
{
  "document_type": "Non-Disclosure Agreement",
  "text": "NON-DISCLOSURE AGREEMENT\n\n...",
  "format": "docx"
}
```

## 10. Docker

Build:

```bash
docker compose build
```

Run:

```bash
docker compose up
```

Then:

- Backend: http://localhost:8000
- Frontend: http://localhost:8501

Put your Gemini key in `.env`.

## Notes on the source documentation

The supplied specification describes `gemini-1.5-pro` and `google-generativeai`. Those are historical choices. The code intentionally keeps the requested Gemini architecture but uses Google's current `google-genai` SDK and a configurable model name. This avoids hard-coding an obsolete SDK/model while preserving the project's intended functionality.
