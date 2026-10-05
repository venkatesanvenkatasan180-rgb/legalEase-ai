import base64

from fastapi import APIRouter, HTTPException

from backend.dependencies import get_settings
from backend.schemas import (
    DocumentRequest,
    ExportRequest,
    GeneratedDocument,
    ExportResponse,
)
from backend.services.document_service import DocumentService
from backend.utils.formatters import format_document

router = APIRouter()


@router.get("/health")
def health():
    settings = get_settings()

    return {
        "status": "ok",
        "service": "LegalEase API",
        "demo_mode": settings.demo_mode,
        "model": settings.gemini_model,
    }


@router.post("/generate", response_model=GeneratedDocument)
def generate(request: DocumentRequest):
    settings = get_settings()

    try:
        text, demo = DocumentService(settings).generate(request)

        return GeneratedDocument(
            document_type=request.document_type,
            text=text,
            demo_mode=demo,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Document generation failed: {exc}",
        ) from exc


@router.post("/export", response_model=ExportResponse)
def export_document(request: ExportRequest):
    try:
        # ----------------------------------------------------
        # Convert uploaded logo from Base64 to bytes
        # ----------------------------------------------------

        logo_bytes = None

        if request.logo_base64:
            try:
                logo_bytes = base64.b64decode(
                    request.logo_base64
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid logo image data.",
                ) from exc

        # ----------------------------------------------------
        # Create formatted document
        # ----------------------------------------------------

        content, content_type, filename = format_document(
            request.text,
            request.document_type,
            request.format,
            logo_bytes,
        )

        # ----------------------------------------------------
        # Convert output to Base64
        # ----------------------------------------------------

        encoded = base64.b64encode(content).decode("ascii")

        return ExportResponse(
            filename=filename,
            content_type=content_type,
            data_base64=encoded,
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {exc}",
        ) from exc
