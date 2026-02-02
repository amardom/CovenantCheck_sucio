from app.core.z3engine import verify_logics

class Deal:
    def __init__(self, id):
        self.id = id
        self.history = {}

    def process_logics_and_cfo_data(self, year, quarter, logics, cfo_data):

        assert isinstance(year, str), "YEAR_NOT_STR"
        assert len(year) == 4, "YEAR_FORMAT_INVALID"
        assert isinstance(quarter, str), "QUARTER_NOT_STR"
        assert quarter in ["Q1", "Q2", "Q3", "Q4"], "QUARTER_FORMAT_INVALID"

        if year not in self.history:
            self.history[year] = {
                "Q1": None, "Q2": None, "Q3": None, "Q4": None
            }

        z3_result = verify_logics(logics, cfo_data)
        
        self.history[year][quarter] = {
            "logics": logics,
            "cfo_data": cfo_data,
            "z3_result": z3_result
        }