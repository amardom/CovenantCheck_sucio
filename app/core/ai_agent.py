import google.generativeai as genai
import json
import os
import re

class CovenantAIAgent:
    def __init__(self, api_key: str):
        # Setup Gemini
        genai.configure(api_key=api_key)
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
        3. Identify the threshold (e.g., 3.0) and operator ('le' for <=, 'ge' for >=).
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "threshold": float,
            "operator": "le" | "ge",
            "recipe": [
                {{ "target": "TOTAL_NET_DEBT", "components": [ {{ "name": "str", "weight": 1/-1 }} ] }},
                {{ 
                  "target": "ADJUSTED_EBITDA", 
                  "components": [ 
                    {{ "name": "str", "weight": 1, "cap_type": "relative", "cap_percentage": 0.10, "cap_reference": "ADJUSTED_EBITDA" }} 
                  ] 
                }},
                {{ "target": "FINAL_RATIO", "op": "div", "args": ["TOTAL_NET_DEBT", "ADJUSTED_EBITDA"] }}
            ]
        }}
        """

        response = self.model.generate_content(prompt)
        
        # Clean the response to ensure it only contains JSON
        text_content = response.text
        json_match = re.search(r'\{.*\}', text_content, re.DOTALL)
        
        if json_match:
            return json.loads(json_match.group())
        raise ValueError("Gemini failed to return a valid JSON recipe.")