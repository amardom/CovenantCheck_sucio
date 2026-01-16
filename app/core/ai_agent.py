import google.generativeai as genai
from google.generativeai import types
import json

class CovenantAIAgent:
    def __init__(self, api_key: str):
        # CONFIGURACIÓN TÉCNICA:
        # transport='rest' evita que la SDK se quede colgada en túneles gRPC.
        genai.configure(api_key=api_key, transport='rest')
        self.model_name = 'gemini-3-flash-preview'
        
        # Esquema de respuesta estricto para asegurar compatibilidad con Z3
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
        """Pass 1: Navigator - Localiza las páginas de interés."""
        print(f"[DEBUG] Navigator analizando esqueleto ({len(pdf_skeleton)} caracteres)...")
        
        prompt = f"""
        Analyze these headers: {pdf_skeleton}.
        Identify page numbers for:
        1. Financial Definitions (EBITDA, Debt).
        2. Covenants (Leverage Ratio).
        
        Return ONLY JSON: {{"definitions_pages": [num], "covenants_pages": [num]}}
        """
        
        # Desactivamos filtros para evitar bloqueos por palabras financieras
        safety = [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
        model = genai.GenerativeModel(self.model_name)
        
        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
                safety_settings=safety
            )
            data = json.loads(response.text)
            # Fail-safe para documentos cortos
            if not data.get("definitions_pages"): data["definitions_pages"] = [1]
            if not data.get("covenants_pages"): data["covenants_pages"] = [1]
            return data
        except Exception as e:
            print(f"[WARNING] Navigator falló, usando default página 1: {e}")
            return {"definitions_pages": [1], "covenants_pages": [1]}

    def generate_recipe(self, combined_text: str):
        """Pass 2: Architect - Extrae la lógica matemática."""
        print(f"[DEBUG] Architect procesando {len(combined_text)} caracteres...")
        
        prompt = f"""
        Extract the mathematical covenant logic from this text:
        {combined_text}

        STRICT RULES:
        1. Use 'le' for maximum/shall not exceed. Use 'ge' for minimum.
        2. For 10% caps, use cap_type='relative', cap_percentage=0.1, cap_reference='adjusted_ebitda'.
        3. Targets must be: 'total_net_debt', 'adjusted_ebitda', and 'final_ratio'.
        4. Netting: Borrowings less cash means cash has weight -1.0.
        """

        model = genai.GenerativeModel(self.model_name)
        
        # Bloqueamos cualquier filtro de seguridad que cause cuelgues (Hang)
        safety = [
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}
        ]

        try:
            response = model.generate_content(
                prompt,
                generation_config=types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=self.recipe_schema,
                    temperature=0.0 # Rapidez máxima
                ),
                safety_settings=safety
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[ERROR] Fallo crítico en Architect: {e}")
            raise e