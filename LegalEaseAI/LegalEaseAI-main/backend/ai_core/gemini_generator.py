from __future__ import annotations

from backend.dependencies import Settings
from backend.schemas import DocumentRequest


class GeminiDocumentGenerator:
    """Generate legal-document drafts using the Google Gemini API."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not self.settings.gemini_api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY is not configured. Set it in .env or enable DEMO_MODE=true."
                )
            from google import genai
            self._client = genai.Client(api_key=self.settings.gemini_api_key)
        return self._client

    def build_prompt(self, request: DocumentRequest) -> str:
        terms = "\n".join(f"- {term}" for term in request.terms) or "- No additional terms supplied."
        jurisdiction = request.jurisdiction or "Not specified"

        return f"""
You are LegalEase's legal-document drafting assistant.

Create a professional DRAFT of the requested legal document from the supplied facts.

IMPORTANT:
- This is an AI-generated draft, not legal advice.
- Do not invent names, dates, monetary values, obligations, statutes, citations, addresses, or facts.
- If a required legal detail is missing, use a neutral placeholder such as [TO BE COMPLETED] rather than inventing it.
- Do not claim that the document is legally valid or enforceable.
- Keep the user's supplied facts and terms intact.
- Use clear formal language.
- Organize the document with a title and numbered section headings.
- Include signature blocks where appropriate.
- Do not wrap the answer in Markdown code fences.
- Do not add commentary before or after the document.

Document type:
{request.document_type}

Parties:
{request.parties}

Effective date:
{request.effective_date}

Jurisdiction:
{jurisdiction}

Requested terms:
{terms}

Additional instructions:
{request.additional_instructions or "None"}

Return only the document draft.
""".strip()

    def generate_document(self, request: DocumentRequest) -> str:
        from google.genai import types

        response = self.client.models.generate_content(
            model=self.settings.gemini_model,
            contents=self.build_prompt(request),
            config=types.GenerateContentConfig(
                temperature=0.25,
                max_output_tokens=12_000,
            ),
        )
        text = getattr(response, "text", None)
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response.")
        return text.strip()

    def generate_demo_document(self, request: DocumentRequest) -> str:
        terms = request.terms or ["Confidentiality and other agreed obligations"]
        term_lines = "\n".join(
            f"{index}. {term}" for index, term in enumerate(terms, start=1)
        )
        return f"""AI-GENERATED DEMO DRAFT — NOT LEGAL ADVICE

{request.document_type.upper()}

Effective Date: {request.effective_date}

PARTIES

{request.parties}

1. PURPOSE

This sample document records the parties' stated intentions for the requested {request.document_type}. It is provided for interface and testing purposes only.

2. AGREED TERMS

{term_lines}

3. GENERAL PROVISIONS

The parties should review all provisions, applicable law, definitions, notice requirements, termination provisions, dispute-resolution provisions, and signature requirements before use.

4. SIGNATURES

Party 1: ______________________________
Name: _________________________________
Date: __________________________________

Party 2: ______________________________
Name: _________________________________
Date: __________________________________

Jurisdiction: {request.jurisdiction or "[TO BE COMPLETED]"}
"""
