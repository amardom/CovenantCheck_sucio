import pymupdf

class PDFContractReader:
    def __init__(self, file_path):
        """
        Initializes the reader with the path to the PDF contract.
        """
        self.file_path = file_path

    def get_skeleton(self):
        """
        Extracts a lightweight version of the PDF (first lines of each page)
        to help the AI identify where the definitions and covenants are located.
        """
        try:
            doc = pymupdf.open(self.file_path)
            skeleton = ""
            for i, page in enumerate(doc):
                # Extract text and take only the first 200 characters for the skeleton
                text = page.get_text().strip()
                preview = text[:200].replace('\n', ' ')
                skeleton += f"Page {i+1}: {preview}...\n"
            doc.close()
            return skeleton
        except Exception as e:
            print(f"[ERROR] Could not read PDF skeleton: {e}")
            return ""

    def extract_pages(self, page_numbers):
        """
        Extracts the full text content from specific page numbers.
        """
        try:
            doc = pymupdf.open(self.file_path)
            content = ""
            for p in page_numbers:
                # Page numbers in pymupdf are 0-indexed
                if 0 < p <= len(doc):
                    content += f"--- PAGE {p} ---\n"
                    content += doc[p-1].get_text()
            doc.close()
            return content
        except Exception as e:
            print(f"[ERROR] Could not extract pages {page_numbers}: {e}")
            return ""