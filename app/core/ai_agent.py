import google.generativeai as genai
from google.generativeai import types
import json
import re

class CovenantAIAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Using your confirmed available model from diagnosis
        self.model_name = 'gemini-3-flash-preview'
        
        # Define the STRICT JSON schema for Z3
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
                            "components": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "weight": {"type": "number"},
                                        # FORCE THE TYPE ENUM
                                        "cap_type": {"type": "string", "enum": ["none", "relative"]},
                                        "cap_percentage": {"type": "number"},
                                        "cap_reference": {"type": "string"}
                                    },
                                    "required": ["name", "weight", "cap_type"]
                                }
                            }
                        }
                    }
                }
            }
        }

    def generate_recipe(self, defs_text: str, covs_text: str):
        prompt = f"""
        Extract financial covenant logic. 
        RULES:
        1. Variable names must be strictly snake_case (e.g., 'operating_profit').
        2. Identify components for 'total_net_debt' and 'adjusted_ebitda'.
        3. If a component is capped (e.g. 10% of EBITDA), include 'cap_percentage': 0.1 and 'cap_reference': 'adjusted_ebitda'.
        
        DEFINITIONS: {defs_text}
        COVENANTS: {covs_text}
        """

        # Enforce the schema via generation_config
        response = genai.GenerativeModel(self.model_name).generate_content(
            prompt,
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.schema
            )
        )

        return json.loads(response.text)