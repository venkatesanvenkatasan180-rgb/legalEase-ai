from __future__ import annotations

import base64
import os
from html import escape

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title { text-align:center; font-size:2.2rem; font-weight:700; margin-bottom:0.2rem; }
    .subtitle { text-align:center; color:#777; margin-bottom:1.5rem; }
    .preview {
        background:#161a1d; color:#f1f3f5; padding:1.25rem; border-radius:12px;
        max-height:600px; overflow:auto; white-space:pre-wrap;
        font-family:Georgia, serif; line-height:1.6;
    }
    .notice { padding:0.8rem 1rem; border-radius:8px; background:#fff3cd; color:#664d03; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">⚖️ LegalEase</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-assisted legal document drafting, editing, and export</div>',
    unsafe_allow_html=True,
)

st.info(
    "LegalEase creates AI-assisted drafts for general informational purposes. "
    "Review the final document with a qualified legal professional before signing or relying on it."
)

if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "document_type" not in st.session_state:
    st.session_state.document_type = "Employment Contract"

left, right = st.columns([1, 1])

with left:
    st.subheader("Document details")
    document_type = st.text_input(
        "Document type",
        value=st.session_state.document_type,
        placeholder="e.g. Non-Disclosure Agreement",
    )
    parties = st.text_area(
        "Parties involved",
        placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
        height=120,
    )
    terms_raw = st.text_area(
        "Terms & conditions",
        placeholder="Payment within 30 days; Confidentiality for 2 years; Either party may terminate with 15 days notice",
        height=150,
        help="Separate each term with a semicolon.",
    )
    effective_date = st.text_input(
        "Effective date",
        placeholder="September 24, 2026",
    )
    jurisdiction = st.text_input(
        "Jurisdiction (optional)",
        placeholder="e.g. India, Tamil Nadu",
    )
    additional = st.text_area(
        "Additional instructions (optional)",
        placeholder="Use clear section headings and plain but formal language.",
        height=100,
    )

    logo = st.file_uploader(
        "Optional logo",
        type=["png", "jpg", "jpeg"],
        help="Logo is used for exported branded documents.",
    )

    generate = st.button("Generate Document", type="primary", use_container_width=True)

with right:
    st.subheader("Document preview")

    if generate:
        if not document_type.strip() or not parties.strip() or not effective_date.strip():
            st.error("Please provide document type, parties, and effective date.")
        else:
            payload = {
                "document_type": document_type.strip(),
                "parties": parties.strip(),
                "terms": [x.strip() for x in terms_raw.split(";") if x.strip()],
                "effective_date": effective_date.strip(),
                "jurisdiction": jurisdiction.strip(),
                "additional_instructions": additional.strip(),
            }

            try:
                with st.spinner("Generating draft..."):
                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json=payload,
                        timeout=TIMEOUT,
                    )
                if response.ok:
                    data = response.json()
                    st.session_state.document_text = data["text"]
                    st.session_state.document_type = data["document_type"]
                    if data.get("demo_mode"):
                        st.warning("Demo mode is enabled. This is a sample draft, not an LLM response.")
                    else:
                        st.success("Draft generated.")
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                    except Exception:
                        detail = response.text
                    st.error(f"Backend error: {detail}")
            except requests.RequestException as exc:
                st.error(f"Could not reach FastAPI at {BACKEND_URL}: {exc}")

    if st.session_state.document_text:
        st.markdown(
            f'<div class="preview">{escape(st.session_state.document_text)}</div>',
            unsafe_allow_html=True,
        )

        if st.button("Click to Edit Document", use_container_width=True):
            st.session_state.editing = True

        if st.session_state.get("editing", False):
            edited = st.text_area(
                "Editable document",
                value=st.session_state.document_text,
                height=500,
            )
            if st.button("Save edits", type="primary"):
                st.session_state.document_text = edited
                st.session_state.editing = False
                st.rerun()

        st.markdown("### Download")
        col1, col2, col3 = st.columns(3)

        for col, fmt, label in [
            (col1, "txt", "TXT"),
            (col2, "docx", "DOCX"),
            (col3, "pdf", "PDF"),
        ]:
            with col:
                if st.button(f"Prepare {label}", use_container_width=True):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/export",
                            json={
                                "document_type": st.session_state.document_type,
                                "text": st.session_state.document_text,
                                "format": fmt,
                            },
                            timeout=TIMEOUT,
                        )
                        if response.ok:
                            data = response.json()
                            st.session_state[f"download_{fmt}"] = (
                                data["filename"],
                                data["content_type"],
                                base64.b64decode(data["data_base64"]),
                            )
                        else:
                            st.error(response.text)
                    except requests.RequestException as exc:
                        st.error(f"Export failed: {exc}")

        for fmt in ["txt", "docx", "pdf"]:
            item = st.session_state.get(f"download_{fmt}")
            if item:
                filename, content_type, content = item
                st.download_button(
                    f"Download {fmt.upper()}",
                    data=content,
                    file_name=filename,
                    mime=content_type,
                    key=f"download_button_{fmt}",
                )
    else:
        st.caption("Your generated document will appear here.")
