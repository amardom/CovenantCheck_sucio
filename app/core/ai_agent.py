import google.generativeai as genai
from google.generativeai import types
import json

class CovenantAIAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model_name = 'gemini-3-flash-preview'
        # Preserving your battle-hardened schema
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
        """Pass 1: Navigator - Robust for single-page and multi-page contracts."""
        prompt = f"""
        Analyze these PDF page headers:
        {pdf_skeleton}

        Identify page numbers for:
        1. Financial Definitions (Adjusted EBITDA, Total Net Debt).
        2. Financial Covenants (Leverage Ratio limits).

        CRITICAL INSTRUCTIONS:
        - If the document is short, both sections may be on the SAME PAGE. 
        - If they are on the same page, include that page number in BOTH lists.
        - Do not return an empty list if the section is visible in the text.

        Return ONLY a JSON: {{"definitions_pages": [num], "covenants_pages": [num]}}
        """
        
        # SAFETY FIX: Disable filters for financial/legal analysis
        safety_settings = [
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        ]

        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json"},
            safety_settings=safety_settings
        )
        return json.loads(response.text)

    def generate_recipe(self, combined_text: str):
        """Pass 2: Architect - Preserving STRICT RULES and safety filters."""
        prompt = f"""
        Extract the mathematical covenant logic from this contract text:
        {combined_text}

        AVAILABLE CFO LABELS:
        - bonds, bank_loans, cash_and_cash_equivalents
        - operating_profit, interest_expense, depreciation_and_amortization
        - extraordinary_restructuring_costs

        STRICT RULES:
        1. OPERATOR: Use 'le' for "shall not exceed" or "maximum". Use 'ge' for "at least" or "minimum".
        2. PERCENTAGES: For "10% of Adjusted EBITDA", use cap_type='relative', cap_percentage=0.1, and cap_reference='adjusted_ebitda'.
        3. TARGET NAMES: Use 'total_net_debt' and 'adjusted_ebitda' as targets for the sums, and 'final_ratio' for the final division.
        4. NETTING: If a definition says "Borrowings less Cash", 'cash_and_cash_equivalents' must have weight: -1.0.
        """
        
        safety_settings = [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]

        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(
            prompt,
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.recipe_schema,
                temperature=0.1
            ),
            safety_settings=safety_settings
        )
        return json.loads(response.text)