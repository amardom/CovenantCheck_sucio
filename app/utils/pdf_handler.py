import pymupdf

class PDFContractReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_skeleton(self):
        doc = pymupdf.open(self.file_path)
        skeleton = ""
        # Leemos solo el índice (primeras 10 páginas)
        for i in range(min(10, len(doc))):
            text = doc[i].get_text()[:200].replace('\n', ' ')
            skeleton += f"Page {i+1}: {text}\n"
        doc.close()
        return skeleton

    def extract_pages(self, page_numbers):
        doc = pymupdf.open(self.file_path)
        content = ""
        for p in page_numbers:
            if 0 < p <= len(doc):
                content += f"\n--- PAGE {p} ---\n"
                content += doc[p-1].get_text()
        doc.close()
        return content

    def extract_relevant_context(self, keywords=["EBITDA", "Leverage Ratio", "Indebtedness"]):
        """
        Busca palabras clave en todo el PDF y devuelve el texto de esas páginas.
        Esto es lo que hace que el sistema sea GENÉRICO.
        """
        doc = pymupdf.open(self.file_path)
        relevant_pages = set()
        
        for i, page in enumerate(doc):
            text = page.get_text().lower()
            if any(key.lower() in text for key in keywords):
                relevant_pages.add(i + 1)
        
        doc.close()
        
        # Ordenamos y limitamos para no saturar a la IA (máximo 15 páginas clave)
        sorted_pages = sorted(list(relevant_pages))
        print(f"[DEBUG] Pages containing keywords: {sorted_pages[:15]}")
        return self.extract_pages(sorted_pages[:15])