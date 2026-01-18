from fpdf import FPDF
import os

def generate_initial_report(data, output_path):
    
    # P = Portrait, mm = millimeters, A4
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Ancho efectivo (Margen de 10mm a cada lado)
    eff_width = pdf.w - 20 

    # --- Header ---
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(eff_width, 10, f"Logical Audit: {data.get('contract_name', 'Unnamed')}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(eff_width, 8, f"Date: {data.get('audit_date', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # --- 1. Variables Inventory ---
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(eff_width, 10, "1. VARIABLE INVENTORY", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    for var in data.get('variables', []):
        pdf.set_font("Helvetica", 'B', 10)
        pdf.write(5, f"{var['name']}: ")
        pdf.set_font("Helvetica", size=10)
        pdf.write(5, f"{var['context']}\n")
    
    pdf.ln(10)

    # --- 2. Logical Rules & Evidence ---
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(eff_width, 10, "2. LOGICAL RULES & EVIDENCE", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    for cond in data.get('logical_conditions', []):
        # Rule ID
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(eff_width, 8, f"Rule {cond['id']}:", new_x="LMARGIN", new_y="NEXT")
        
        # Bloque de Fórmula (Gris)
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font("Arial", "", 9)
        # El truco: new_x="LMARGIN", new_y="NEXT" obliga al cursor a bajar SIEMPRE
        pdf.multi_cell(eff_width, 8, f"  {cond['formula']}  ", border=0, fill=True, align='L', new_x="LMARGIN", new_y="NEXT")
        
        # Bloque de Evidencia (Debajo de la fórmula)
        pdf.set_font("Helvetica", 'I', 9)
        pdf.set_text_color(100, 100, 100)
        evidence_text = f"Source (Page {cond.get('page', 'N/A')}): {cond['evidence']}"
        pdf.multi_cell(eff_width, 5, evidence_text, align='L', new_x="LMARGIN", new_y="NEXT")
        
        # Reset color y espacio entre reglas
        pdf.set_text_color(0, 0, 0)
        pdf.ln(8)

    # Crear carpeta si no existe y guardar
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    pdf.output(output_path)