import json
from pypdf import PdfReader
from app.utils.report_pdf import generate_initial_report, generate_final_report
from app.core.z3_engine import validate_json, verify_logics

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_pdf_metrics(filepath):
    """Extrae métricas cuantitativas del PDF."""
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

def test_pdf_structural_integrity():
    output_pdf = "audit_report_netflix.pdf"
    
    # 1. Ejecutar la generación del PDF (basado en el commit a3f88f)
    path_logic_data = f"tests/scenarios/logics_simple.json"
    logics = load_json(path_logic_data)
    validate_json("logics_simple.json", logics)
    path_cfo_data = f"tests/scenarios/cfo_data_simple.json"
    cfo_data = load_json(path_cfo_data)
    generate_initial_report(logics, output_pdf)
    
    metrics = get_pdf_metrics(output_pdf)
    
    # 2. Valores esperados (estos los sacas de una ejecución que sepas que es correcta)
    # Por ejemplo, para Netflix siempre esperamos:
    EXPECTED_MIN_WORDS = 172  # Un reporte real no debería tener menos de esto
    EXPECTED_PAGES = 1
    
    # 3. Asserts de "Fail Fast"
    assert metrics["pages"] == EXPECTED_PAGES, "El número de páginas ha cambiado inexplicablemente"
    assert metrics["word_count"] == EXPECTED_MIN_WORDS, "El PDF parece estar casi vacío o le falta texto crítico"
    
    # Métrica de consistencia específica:
    # Si tenemos 10 variables en el JSON, el nombre de esas 10 variables 
    # DEBE aparecer al menos una vez en el PDF.
    reader = PdfReader(output_pdf)
    full_text = " ".join([p.extract_text() for p in reader.pages])
    
    #for var in logics["variables"]:
        #assert var["name"] in full_text, f"La variable {var['name']} se perdió en la generación del PDF"

def test_pdf_structural_integrity_final():
    output_pdf = "audit_report_netflix.pdf"
    
    # 1. Ejecutar la generación del PDF (basado en el commit a3f88f)
    path_logic_data = f"tests/scenarios/logics_simple.json"
    logics = load_json(path_logic_data)
    validate_json("logics_simple.json", logics)
    path_cfo_data = f"tests/scenarios/cfo_data_simple.json"
    cfo_data = load_json(path_cfo_data)

    z3_result = verify_logics(logics, cfo_data)
    generate_final_report(z3_result, logics, cfo_data, output_pdf)
    
    metrics = get_pdf_metrics(output_pdf)
    
    # 2. Valores esperados (estos los sacas de una ejecución que sepas que es correcta)
    # Por ejemplo, para Netflix siempre esperamos:
    EXPECTED_MIN_WORDS = 64  # Un reporte real no debería tener menos de esto
    EXPECTED_PAGES = 1
    
    # 3. Asserts de "Fail Fast"
    assert metrics["pages"] == EXPECTED_PAGES, "El número de páginas ha cambiado inexplicablemente"
    assert metrics["word_count"] == EXPECTED_MIN_WORDS, "El PDF parece estar casi vacío o le falta texto crítico"
    
    # Métrica de consistencia específica:
    # Si tenemos 10 variables en el JSON, el nombre de esas 10 variables 
    # DEBE aparecer al menos una vez en el PDF.
    reader = PdfReader(output_pdf)
    full_text = " ".join([p.extract_text() for p in reader.pages])
    
    for var in logics["variables"]:
        assert var["name"] in full_text, f"La variable {var['name']} se perdió en la generación del PDF"