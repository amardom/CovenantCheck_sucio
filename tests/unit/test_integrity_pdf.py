import json
from pypdf import PdfReader
from app.core.report import generate_initial_report, generate_final_report, generate_portfolio_report
from app.core.z3engine import validate_json, verify_logics
from app.core.portfolio import create_portfolio

LOGICS_FILENAME = "logics_simple.json"
PATH_LOGICS = "tests/scenarios/" + LOGICS_FILENAME
PATH_CFO_DATA = "tests/scenarios/cfo_data_simple.json"

OUTPUT_INITIAL_PDF = "test_initial_report.pdf"
OUTPUT_FINAL_PDF = "test_final_report.pdf"

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_pdf_metrics(filepath):
    reader = PdfReader(filepath)
    text_content = ""
    total_words = 0
    
    for page in reader.pages:
        page_text = page.extract_text()
        text_content += page_text
        total_words += len(page_text.split())
    
    return {
        "pages": len(reader.pages),
        "word_count": total_words,
        "char_count": len(text_content)
    }

def assert_variables(logics, output_pdf):
    reader = PdfReader(output_pdf)
    full_text = " ".join([p.extract_text() for p in reader.pages])
    
    for var in logics["variables"]:
        assert var["name"] in full_text
    
def test_pdf_structural_integrity_initial():
    
    logics = load_json(PATH_LOGICS)
    validate_json(logics)

    generate_initial_report(logics, OUTPUT_INITIAL_PDF)
    
    metrics = get_pdf_metrics(OUTPUT_INITIAL_PDF)
    
    EXPECTED_PAGES = 1
    EXPECTED_WORDS = 170
    EXPECTED_CHARS = 1444
    
    assert metrics["pages"] == EXPECTED_PAGES
    assert metrics["word_count"] == EXPECTED_WORDS
    assert metrics["char_count"] == EXPECTED_CHARS

    assert_variables(logics, OUTPUT_INITIAL_PDF)

def test_pdf_structural_integrity_final():
    
    logics = load_json(PATH_LOGICS)
    validate_json(logics)

    cfo_data = load_json(PATH_CFO_DATA)
    z3_result = verify_logics(logics, cfo_data)

    generate_final_report(z3_result, logics, cfo_data, OUTPUT_FINAL_PDF)
    
    metrics = get_pdf_metrics(OUTPUT_FINAL_PDF)
    
    EXPECTED_PAGES = 1
    EXPECTED_WORDS = 62
    EXPECTED_CHARS = 669
    
    assert metrics["pages"] == EXPECTED_PAGES
    assert metrics["word_count"] == EXPECTED_WORDS
    assert metrics["char_count"] == EXPECTED_CHARS
    
    assert_variables(logics, OUTPUT_FINAL_PDF)

def test_pdf_structural_integrity_executive_summary():

    clients = ["TechCorp", "HealthCorp"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    portfolio = create_portfolio(clients, years, quarters, root_path="tests/scenarios/Fund_01")

    ANALYSIS_CONFIG = {
        "TechCorp": ["leverage_ratio", "ebitda"],
        "HealthCorp": ["leverage_ratio", "ebitda"]
    }

    generate_portfolio_report(portfolio, ANALYSIS_CONFIG, output_path="tests/scenarios/Fund_01/portfolio_executive_summary.pdf")
    
    metrics = get_pdf_metrics("tests/scenarios/Fund_01/portfolio_executive_summary.pdf")
    
    EXPECTED_PAGES = 1
    EXPECTED_WORDS = 89
    EXPECTED_CHARS = 489
    
    assert metrics["pages"] == EXPECTED_PAGES
    assert metrics["word_count"] == EXPECTED_WORDS
    assert metrics["char_count"] == EXPECTED_CHARS
    