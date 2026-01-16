import google.generativeai as genai
from google.generativeai import types
import json

class CovenantAIAgent:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key is missing")
        
        genai.configure(api_key=api_key)
        # Usamos el modelo confirmado en tu diagnóstico
        self.model_name = 'gemini-3-flash-preview'
        
        # Definición estricta del Schema
        self.schema = {
            "type": "object",
            "properties": {
                "threshold": {"type": "number"},
                "operator": {"type": "string", "enum": ["le", "ge"]},
                "recipe": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "description": "Nombre de la variable resultado (ej: adjusted_ebitda)"},
                            "op": {"type": "string", "enum": ["sum", "div"], "description": "Operación a realizar"},
                            "args": {
                                "type": "array", 
                                "items": {"type": "string"},
                                "description": "Lista de variables para la operación 'div' (numerador y denominador)"
                            },
                            "components": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "weight": {"type": "number"},
                                        "cap_type": {"type": "string", "enum": ["none", "relative"]},
                                        "cap_percentage": {
                                            "type": "number", 
                                            "description": "Decimal value. 10% MUST be 0.1, 20% MUST be 0.2"
                                        },
                                        "cap_reference": {"type": "string", "description": "Variable base para el cap (ej: adjusted_ebitda)"}
                                    },
                                    "required": ["name", "weight", "cap_type"]
                                }
                            }
                        },
                        "required": ["target", "op"]
                    }
                }
            },
            "required": ["threshold", "operator", "recipe"]
        }

    def generate_recipe(self, defs_text: str, covs_text: str):
        # El prompt ahora es más directo para evitar bucles
        prompt = f"""
        Extract financial covenant logic from the text below into a structured JSON recipe.
        
        CFO LABELS (Use these for components): 
        [bonds, bank_loans, cash_and_cash_equivalents, operating_profit, interest_expense, depreciation_and_amortization, extraordinary_restructuring_costs]
        
        STRICT RULES:
        1. Only use the CFO LABELS provided above.
        2. Identify the formula for 'total_net_debt' and 'adjusted_ebitda'.
        3. 'extraordinary_restructuring_costs' has a 10% cap relative to 'adjusted_ebitda'.
        4. The LAST item in the recipe must be 'final_ratio' using 'op': 'div'.
        5. Percentages MUST be decimals (10% = 0.1).
        
        TEXTS:
        Definitions: {defs_text}
        Covenants: {covs_text}
        """

        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(
            prompt,
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.schema,
                temperature=0.1 # Bajamos la temperatura para mayor precisión y evitar bucles
            )
        )
        
        return json.loads(response.text)