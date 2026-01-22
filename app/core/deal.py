import json
from pathlib import Path
from app.core.z3_engine import validate_json, verify_logics

FILENAME_LOGICS = "logics.json"
FILENAME_CFO_DATA = "cfo_data.json"

class Deal:
    def __init__(self, deal_id):
        self.id = deal_id
        
        # Diccionario dinámico: { "2024": {"Q1": {...}, "Q2": {...}}, "2025": {...} }
        self.history = {}

    def process_logics_and_cfodata(self, year, quarter, base_path):

        year_str = str(year)
        
        if year_str not in self.history:
            self.history[year_str] = {
                "Q1": None, "Q2": None, "Q3": None, "Q4": None
            }

        path = Path(f"{base_path}{self.id}/{year_str}_{quarter}")

        with open(path / FILENAME_LOGICS, "r") as f:
            logics = json.load(f)
        validate_json(FILENAME_LOGICS, logics)

        with open(path / FILENAME_CFO_DATA, "r") as f:
            cfo_data = json.load(f)

        # Ejecutar motor lógico
        z3_result = verify_logics(logics, cfo_data)
        
        # Guardar todo el paquete de información
        self.history[year_str][quarter] = {
            "logics": logics,
            "cfo_data": cfo_data,
            "z3_result": z3_result
        }