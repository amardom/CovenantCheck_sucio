import pymupdf

class PDFContractReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_relevant_context(self, custom_keywords=None):
        # Lista maestra profesional para cubrir cualquier tipo de contrato (LMA, NY Law, etc.)
        keywords = custom_keywords or [
            "EBITDA", "Net Income", "Operating Profit", "Interest Expense", 
            "Depreciation", "Amortization", "Add-backs", "Restructuring",
            "Indebtedness", "Total Debt", "Borrowings", "Notes Payable", 
            "Capital Leases", "Letters of Credit", "Guarantees",
            "Financial Covenant", "Leverage Ratio", "Fixed Charge", 
            "Net Debt", "Unrestricted Cash", "Cash Equivalents"
        ]
        
        doc = pymupdf.open(self.file_path)
        relevant_pages = set()
        
        for i, page in enumerate(doc):
            text = page.get_text().lower()
            if any(key.lower() in text for key in keywords):
                # Aplicamos la "Ventana de Contexto": Página anterior, actual y siguiente
                if i > 0: relevant_pages.add(i)
                relevant_pages.add(i + 1)
                if i < len(doc) - 1: relevant_pages.add(i + 2)
        
        doc.close()
        
        # Ordenamos y limitamos para eficiencia (Gemini maneja bien hasta 20-30 páginas)
        sorted_pages = sorted(list(relevant_pages))
        print(f"[DEBUG] Scanning {len(sorted_pages)} context-rich pages...")
        
        return self.extract_pages(sorted_pages)

    def extract_pages(self, page_numbers):
        doc = pymupdf.open(self.file_path)
        content = ""
        for p in page_numbers:
            if 0 < p <= len(doc):
                content += f"\n--- PAGE {p} ---\n{doc[p-1].get_text()}"
        doc.close()
        return content