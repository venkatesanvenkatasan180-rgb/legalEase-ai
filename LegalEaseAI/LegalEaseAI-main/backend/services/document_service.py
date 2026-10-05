from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from backend.dependencies import Settings
from backend.schemas import DocumentRequest


class DocumentService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.generator = GeminiDocumentGenerator(settings)

    def generate(self, request: DocumentRequest) -> tuple[str, bool]:
        total_chars = len(request.model_dump_json())
        if total_chars > self.settings.max_input_chars:
            raise ValueError("Input is too large. Please shorten the supplied content.")

        if self.settings.demo_mode:
            return self.generator.generate_demo_document(request), True

        return self.generator.generate_document(request), False
