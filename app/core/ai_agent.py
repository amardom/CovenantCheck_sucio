import anthropic
import json

class CovenantAIAgent:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_recipe(self, defs_text, covs_text):
        # Step 1 & 2 combined in a single prompt with high-level structure 
        # to maintain context of the definitions while applying the covenant rule.
        prompt = f"""
        TASK: Extract financial covenant logic.
        
        SECTION 1 (DEFINITIONS):
        {defs_text}
        
        SECTION 2 (COVENANTS):
        {covs_text}
        
        INSTRUCTIONS:
        1. Define 'TOTAL_NET_DEBT' and 'ADJUSTED_EBITDA' based on Section 1.
        2. Identify any percentage-based caps (e.g., add-backs limited to 10% of EBITDA).
        3. Identify the threshold and operator from Section 2.
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "threshold": 3.0,
            "operator": "le",
            "recipe": [
                {{ "target": "TOTAL_NET_DEBT", "components": [...] }},
                {{ "target": "ADJUSTED_EBITDA", "components": [...] }},
                {{ "target": "FINAL_RATIO", "op": "div", "args": ["TOTAL_NET_DEBT", "ADJUSTED_EBITDA"] }}
            ]
        }}
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.content[0].text)