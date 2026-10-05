from typing import Literal

from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=120)
    parties: str = Field(min_length=2, max_length=8_000)
    terms: list[str] = Field(default_factory=list, max_length=50)
    effective_date: str = Field(min_length=2, max_length=100)
    jurisdiction: str = Field(default="", max_length=200)
    additional_instructions: str = Field(default="", max_length=8_000)

    @field_validator("terms")
    @classmethod
    def clean_terms(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class GeneratedDocument(BaseModel):
    document_type: str
    text: str
    demo_mode: bool = False


class ExportRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=120)
    text: str = Field(min_length=1, max_length=100_000)
    format: Literal["txt", "docx", "pdf"]
    logo_base64: str | None = None


class ExportResponse(BaseModel):
    filename: str
    content_type: str
    data_base64: str