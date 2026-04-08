import os
import uuid
import traceback
from typing import List
from PIL import Image
from pdf2image import convert_from_path
from google import genai
from google.genai import types
from schema import DocumentResponse, DocumentFields

class DocumentProcessor:
    def __init__(self):
        # Requires GOOGLE_API_KEY environment variable to be set
        self.client = genai.Client()
        # Using 1.5 Pro as it is best-in-class for complex document reasoning
        self.model_name = "gemini-2.5-flash" 

    def _prepare_document(self, file_path: str) -> List[Image.Image]:
        """Converts PDFs to images to normalize scanned vs. typed data."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = file_path.lower().split('.')[-1]
        if ext == 'pdf':
            # Convert PDF pages to PIL Images
            return convert_from_path(file_path, dpi=200, poppler_path=r'C:\poppler\Library\bin')
        elif ext in ['png', 'jpg', 'jpeg', 'tiff']:
            return [Image.open(file_path)]
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def process(self, file_path: str) -> DocumentResponse:
        """Main invokable function that returns the required JSON structure."""
        doc_id = str(uuid.uuid4())
        
        try:
            images = self._prepare_document(file_path)
            
            prompt = """
            Analyze the provided document images. 
            1. Identify the document category and specific type. 
            2. Extract the required fields: primary legal name, structured address, issue/effective date, expiry date (if any), and all monetary amounts.
            3. Provide realistic confidence scores (0.0 to 1.0). Deduct confidence if text is handwritten, blurry, faded, or rotated.
            4. Extract the exact 'source_text' from the document that justifies your extraction.
            5. Flag any physical issues with the document (e.g., 'faded stamp', 'rotated', 'mixed languages') in the 'flags' array.
            """

            # Combine the text prompt with the image array
            contents = [prompt] + images

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DocumentResponse,
                    temperature=0.1 # Low temp for factual extraction
                ),
            )

            # Parse the LLM's JSON output back into our Pydantic model
            result = DocumentResponse.model_validate_json(response.text)
            result.document_id = doc_id
            return result

        except Exception as e:
            # Graceful failure handling: Return the schema with errors populated
            return DocumentResponse(
                document_id=doc_id,
                category="Unknown",
                type="Unknown",
                language="Unknown",
                confidence=0.0,
                fields=DocumentFields(),
                flags=["Processing failed"],
                processing_errors=[str(e), traceback.format_exc()]
            )