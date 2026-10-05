from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

TEXT = """NON-DISCLOSURE AGREEMENT

1. PURPOSE

The parties agree to protect confidential information.

2. TERMS

- Confidentiality applies for two years.
"""


def test_txt_export():
    response = client.post(
        "/export",
        json={"document_type": "NDA", "text": TEXT, "format": "txt"},
    )
    assert response.status_code == 200
    assert response.json()["content_type"].startswith("text/plain")


def test_docx_export():
    response = client.post(
        "/export",
        json={"document_type": "NDA", "text": TEXT, "format": "docx"},
    )
    assert response.status_code == 200
    assert response.json()["filename"].endswith(".docx")


def test_pdf_export():
    response = client.post(
        "/export",
        json={"document_type": "NDA", "text": TEXT, "format": "pdf"},
    )
    assert response.status_code == 200
    assert response.json()["filename"].endswith(".pdf")
