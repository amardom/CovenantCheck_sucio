import google.generativeai as genai
import json
import re

class CovenantAIAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Change 'gemini-1.5-flash' to 'gemini-1.5-flash-latest' 
        # or simply 'gemini-1.5-flash' but ensure the call is standard
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_recipe(self, defs_text: str, covs_text: str):
        prompt = f"""
        TASK: Extract financial covenant logic into a Z3-compatible JSON recipe.
        
        SECTION 1 (DEFINITIONS):
        {defs_text}
        
        SECTION 2 (COVENANTS):
        {covs_text}
        
        INSTRUCTIONS:
        1. Identify components for 'TOTAL_NET_DEBT' and 'ADJUSTED_EBITDA'.
        2. Strictly detect percentage-based caps (e.g., restructuring costs limited to 10% of EBITDA).
        3. Identify the threshold and operator ('le' for <=, 'ge' for >=).
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "threshold": 3.0,
            "operator": "le",
            "recipe": [
                {{ "target": "TOTAL_NET_DEBT", "components": [ {{ "name": "gross_debt", "weight": 1 }} ] }},
                {{ "target": "ADJUSTED_EBITDA", "components": [ {{ "name": "net_income", "weight": 1 }} ] }},
                {{ "target": "FINAL_RATIO", "op": "div", "args": ["TOTAL_NET_DEBT", "ADJUSTED_EBITDA"] }}
            ]
        }}
        """

        # Using the standard generation call
        response = self.model.generate_content(prompt)
        
        # Defensive check for response.text
        try:
            text_content = response.text
        except ValueError:
            # If the response was blocked or empty
            print("Error: The model returned an empty response or was blocked.")
            return None

        json_match = re.search(r'\{.*\}', text_content, re.DOTALL)
        
        if json_match:
            return json.loads(json_match.group())
        raise ValueError("Gemini failed to return a valid JSON recipe.")