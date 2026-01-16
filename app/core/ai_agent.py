import google.generativeai as genai
import json
import re
import os

class CovenantAIAgent:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key is missing!")
        
        genai.configure(api_key=api_key)
        
        # 'gemini-3-flash-preview' is the stable alias. 
        # If this still fails, your API key might not have 'v1beta' access enabled.
        self.model_name = 'gemini-3-flash-preview'
        self.model = genai.GenerativeModel(self.model_name)

    def generate_recipe(self, defs_text: str, covs_text: str):
        prompt = f"""
        TASK: Extract financial covenant logic into a Z3-compatible JSON recipe.
        
        SECTION 1 (DEFINITIONS):
        {defs_text}
        
        SECTION 2 (COVENANTS):
        {covs_text}
        
        INSTRUCTIONS:
        1. Identify components for 'TOTAL_NET_DEBT' and 'ADJUSTED_EBITDA'.
        2. Detect percentage-based caps (e.g., restructuring costs limited to 10% of EBITDA).
        3. Identify the threshold and operator ('le' for <=, 'ge' for >=).
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "threshold": float,
            "operator": "le",
            "recipe": [
                {{ "target": "TOTAL_NET_DEBT", "components": [ {{ "name": "str", "weight": 1 }} ] }},
                {{ "target": "ADJUSTED_EBITDA", "components": [ {{ "name": "str", "weight": 1 }} ] }},
                {{ "target": "FINAL_RATIO", "op": "div", "args": ["TOTAL_NET_DEBT", "ADJUSTED_EBITDA"] }}
            ]
        }}
        """

        try:
            # We call the model. If it fails with 404, we try the 'latest' alias.
            response = self.model.generate_content(prompt)
            text_content = response.text
        except Exception as e:
            if "404" in str(e):
                print(f"Warning: {self.model_name} not found. Trying 'gemini-1.5-flash-latest'...")
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = self.model.generate_content(prompt)
                text_content = response.text
            else:
                raise e

        # Standard JSON extraction logic
        json_match = re.search(r'\{.*\}', text_content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError("Gemini returned content but no valid JSON was found.")