import google.generativeai as genai
from google.generativeai import types
import json

class CovenantAIAgent:
    def __init__(self, api_key: str):
        # We use 'rest' transport to prevent gRPC connection hangs
        genai.configure(api_key=api_key, transport='rest')
        self.model_name = 'gemini-3-flash-preview'
        
        # Robust schema: Focuses on flat parameters to prevent token loops
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
                            "cap_percentage": {"type": "number"}, # e.g., 0.10 for 10%
                            "cap_reference": {"type": "string"}    # e.g., "ebitda"
                        },
                        "required": ["name", "group", "weight"]
                    }
                }
            },
            "required": ["threshold", "operator", "components"]
        }

    def identify_sections(self, pdf_skeleton: str):
        """Pass 0: Locates pages for definitions and covenants."""
        model = genai.GenerativeModel(self.model_name)
        prompt = f"""
        Analyze the following PDF structure:
        {pdf_skeleton}
        
        Identify page numbers for:
        1. Financial Definitions (where Adjusted EBITDA or Net Debt are defined).
        2. Financial Covenants (where the Leverage Ratio limit is stated).
        
        Return ONLY JSON: {{"definitions_pages": [int], "covenants_pages": [int]}}
        """
        
        try:
            response = model.generate_content(
                prompt, 
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception:
            return {"definitions_pages": [1], "covenants_pages": [1]}

    def generate_recipe(self, combined_text: str):
        """Pass 1: Extracts parameters for Z3 logic construction."""
        # Fixed list of labels to ensure alignment with CFO data
        CFO_LABELS = [
            "bonds", "bank_loans", "cash_and_cash_equivalents",
            "operating_profit", "interest_expense", "depreciation_and_amortization",
            "extraordinary_restructuring_costs"
        ]

        prompt = f"""
        TASK: Extract financial covenant parameters from the text.
        ALLOWED LABELS: {", ".join(CFO_LABELS)}

        INSTRUCTIONS:
        1. Map contract terms to ALLOWED LABELS (e.g., 'Borrowings' maps to 'bonds' and 'bank_loans').
        2. Identify the 'threshold' (the limit value) and 'operator' ('le' for maximum, 'ge' for minimum).
        3. Assign each label to either 'debt' or 'ebitda' group.
        4. If a component is capped (e.g., 'Extraordinary costs not to exceed 10% of EBITDA'), 
           set 'cap_percentage' to 0.10 and 'cap_reference' to 'ebitda'.

        CONTRACT TEXT:
        {combined_text}
        """

        model = genai.GenerativeModel(self.model_name)
        
        # Safety settings to BLOCK_NONE to prevent false positives in financial terms
        safety = [
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}
        ]

        response = model.generate_content(
            prompt,
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.recipe_schema,
                temperature=0.0
            ),
            safety_settings=safety
        )
        return json.loads(response.text)