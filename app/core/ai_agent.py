import google.generativeai as genai
from google.generativeai import types
import json

class CovenantAIAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model_name = 'gemini-3-flash-preview'
        
        # Strict Schema (matching your Z3 logic switches)
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
                            "target": {"type": "string"},
                            "op": {"type": "string", "enum": ["sum", "div"]},
                            "args": {"type": "array", "items": {"type": "string"}},
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
                                    },
                                    "required": ["name", "weight", "cap_type"]
                                }
                            }
                        },
                        "required": ["target"]
                    }
                }
            },
            "required": ["threshold", "operator", "recipe"]
        }

    def generate_recipe(self, defs_text: str, covs_text: str):
        # We explicitly tell the AI which labels the CFO uses
        prompt = f"""
        TASK: Extract financial covenant logic into Z3-compatible JSON.
        
        AVAILABLE CFO LABELS: [bonds, bank_loans, cash_and_cash_equivalents, operating_profit, interest_expense, depreciation_and_amortization, extraordinary_restructuring_costs]
        
        RULES:
        1. Only use names from the 'AVAILABLE CFO LABELS' list for components.
        2. MANDATORY: The final item in the 'recipe' array MUST be the 'final_ratio' calculation using 'op': 'div'.
        3. For 'extraordinary_restructuring_costs', apply the 10% limit logic if mentioned.
        
        DOCUMENTS:
        Definitions: {defs_text}
        Covenants: {covs_text}
        """

        response = genai.GenerativeModel(self.model_name).generate_content(
            prompt,
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.schema
            )
        )
        return json.loads(response.text)