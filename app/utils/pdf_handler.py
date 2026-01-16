import fitz  # PyMuPDF

class PDFContractReader:
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extrae todo el texto del PDF y lo limpia mínimamente."""
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text("text") + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""