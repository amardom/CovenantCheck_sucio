from fpdf import FPDF

def generate_minimalist_report(data, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Logic Audit: {data['contract_name']}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Date: {data['audit_date']}", ln=True)
    pdf.ln(5)

    # Section 1: Variables
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. VARIABLE INVENTORY", ln=True)
    pdf.set_font("Arial", size=10)
    
    for var in data['variables']:
        pdf.set_font("Arial", 'B', 10)
        pdf.write(5, f"{var['name']}: ")
        pdf.set_font("Arial", size=10)
        pdf.write(5, f"{var['context']}\n")
    pdf.ln(10)

    # Section 2: Logical Rules (The Blueprint)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. LOGICAL RULES & EVIDENCE", ln=True)
    
    for cond in data['logical_conditions']:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, f"Rule ID: {cond['id']}", ln=True)
        
        # La fórmula es lo más importante
        pdf.set_fill_color(240, 240, 240) # Gris muy claro
        pdf.set_font("Courier", 'B', 11)
        pdf.cell(0, 8, f"  {cond['formula']}  ", ln=True, fill=True)
        
        # Evidencia legal
        pdf.set_font("Arial", 'I', 9)
        pdf.multi_cell(0, 5, f"Source (Page {cond['page']}): {cond['evidence']}")
        pdf.ln(5)

    pdf.output(output_path)
