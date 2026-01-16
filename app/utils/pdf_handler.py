import fitz  # PyMuPDF
import json

class PDFContractReader:
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extrae todo el texto (mantiene compatibilidad con archivos pequeños)."""
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text("text") + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    @staticmethod
    def get_skeleton(pdf_path: str, max_chars_per_page: int = 500) -> str:
        """
        Extrae solo el inicio de cada página para que la IA identifique dónde 
        están las secciones sin leer todo el contenido. Ideal para el 'Navigator'.
        """
        skeleton = []
        try:
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc):
                    # Solo tomamos el principio de la página (títulos/encabezados)
                    page_text = page.get_text("text")[:max_chars_per_page].replace('\n', ' ')
                    skeleton.append(f"Page {page_num + 1}: {page_text}...")
            return "\n".join(skeleton)
        except Exception as e:
            print(f"Error creating skeleton: {e}")
            return ""

    @staticmethod
    def extract_specific_pages(pdf_path: str, page_numbers: list) -> str:
        """
        Extrae el texto completo de una lista de páginas específicas.
        Esto ahorra tokens y evita ruido de páginas irrelevantes.
        """
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for p_num in page_numbers:
                    # fitz usa índice 0, pero los humanos usamos 1
                    if 0 <= p_num - 1 < len(doc):
                        text += doc[p_num - 1].get_text("text") + "\n"
            return text
        except Exception as e:
            print(f"Error extracting specific pages: {e}")
            return ""