import google.generativeai as genai
from google.generativeai import types
import json

class CovenantAIAgent:
    def __init__(self, api_key: str):
        # Usamos transporte 'rest' para mayor estabilidad en procesos largos
        genai.configure(api_key=api_key, transport='rest')
        self.model_name = 'gemini-3-flash-preview'
        
        # Esquema robusto para capturar componentes de EBITDA y Deuda
        self.recipe_schema = {
            "type": "object",
            "properties": {
                "threshold": {"type": "number"},
                "operator": {"type": "string", "enum": ["le", "ge"]},
                "components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "group": {"type": "string", "enum": ["debt", "ebitda"]},
                            "weight": {"type": "number"},
                            "cap_percentage": {"type": "number"},
                            "cap_reference": {"type": "string"}
                        },
                        "required": ["name", "group", "weight"]
                    }
                }
            },
            "required": ["threshold", "operator", "components"]
        }

    def generate_recipe(self, combined_text: str):
        """
        Mapea dinámicamente el lenguaje legal a etiquetas financieras estándar.
        """
        CFO_LABELS = [
            "bonds", "bank_loans", "cash_and_cash_equivalents",
            "operating_profit", "interest_expense", "depreciation_and_amortization",
            "extraordinary_restructuring_costs"
        ]

        prompt = f"""
        TASK: Act as a expert Financial Controller. 
        Extract the mathematical recipe for the 'Consolidated Leverage Ratio' from this Credit Agreement.

        MAPPING RULES:
        1. Map all forms of debt (Revolving Loans, Term Loans, Notes) to 'bank_loans' or 'bonds'.
        2. Map 'Consolidated Net Income' or 'Operating Profit' to 'operating_profit'.
        3. Identify all 'Add-backs' for EBITDA (Depreciation, Interest, etc.).
        4. If you find a limit like 'not to exceed 15% of EBITDA', set 'cap_percentage' to 0.15.

        ALLOWED LABELS: {", ".join(CFO_LABELS)}

        CONTRACT TEXT:
        {combined_text}
        """

        model = genai.GenerativeModel(self.model_name)
        
        # Configuramos la respuesta estructurada
        response = model.generate_content(
            prompt,
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.recipe_schema,
                temperature=0.0
            )
        )
        return json.loads(response.text)

    def identify_sections(self, pdf_skeleton: str):
        """Metodo auxiliar para identificar paginas (opcional si usas extract_relevant_context)"""
        model = genai.GenerativeModel(self.model_name)
        prompt = f"Identify sections in this skeleton:\n{pdf_skeleton}\nReturn ONLY JSON: {{\"definitions_pages\": [int], \"covenants_pages\": [int]}}"
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)