import google.generativeai as genai
from google.generativeai import types
import json

class CovenantAIAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model_name = 'gemini-3-flash-preview'
        
        # Esquema exacto para validación de Z3
        self.recipe_schema = {
            "type": "object",
            "properties": {
                "threshold": {"type": "number"},
                "operator": {"type": "string", "enum": ["le", "ge"]},
                "recipe": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string"},
                            "op": {"type": "string", "enum": ["sum", "div"]},
                            "components": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "weight": {"type": "number"},
                                        "cap_type": {"type": "string", "enum": ["none", "relative"]},
                                        "cap_percentage": {"type": "number"},
                                        "cap_reference": {"type": "string"}
                                    }
                                }
                            },
                            "args": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["target", "op"]
                    }
                }
            },
            "required": ["threshold", "operator", "recipe"]
        }

    def identify_sections(self, pdf_skeleton: str):
        """Pass 1: Navigator - Localiza las páginas clave."""
        prompt = f"""
        Analyze these PDF page headers:
        {pdf_skeleton}

        Identify page numbers for:
        1. Financial Definitions (Adjusted EBITDA, Total Net Debt).
        2. Financial Covenants (Leverage Ratio limits).

        STRICT RULES:
        - If the document is short (1-2 pages), both are usually on page 1.
        - Return ONLY a JSON: {{"definitions_pages": [num], "covenants_pages": [num]}}
        """
        
        safety = [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
        model = genai.GenerativeModel(self.model_name)
        
        response = model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json"},
            safety_settings=safety
        )
        
        try:
            data = json.loads(response.text)
            # Fail-safe: Si la IA devuelve listas vacías en un PDF corto, forzamos página 1
            if not data.get("definitions_pages"): data["definitions_pages"] = [1]
            if not data.get("covenants_pages"): data["covenants_pages"] = [1]
            return data
        except:
            return {"definitions_pages": [1], "covenants_pages": [1]}

    def generate_recipe(self, combined_text: str):
        """Pass 2: Architect - Extrae la lógica matemática con reglas estrictas."""
        prompt = f"""
        Extract the mathematical covenant logic from this text:
        {combined_text}

        AVAILABLE CFO LABELS:
        - bonds, bank_loans, cash_and_cash_equivalents
        - operating_profit, interest_expense, depreciation_and_amortization
        - extraordinary_restructuring_costs

        STRICT RULES:
        1. OPERATOR: Use 'le' for "maximum" or "shall not exceed". Use 'ge' for "minimum".
        2. PERCENTAGES: For "10% of Adjusted EBITDA", use cap_type='relative', cap_percentage=0.1, and cap_reference='adjusted_ebitda'.
        3. TARGET NAMES: Use 'total_net_debt', 'adjusted_ebitda' and 'final_ratio'.
        4. NETTING: If it says "minus Cash", weight must be -1.0.
        """
        
        safety = [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
        model = genai.GenerativeModel(self.model_name)
        
        response = model.generate_content(
            prompt,
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.recipe_schema,
                temperature=0.1
            ),
            safety_settings=safety
        )
        return json.loads(response.text)