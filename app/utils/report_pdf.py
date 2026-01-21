from fpdf import FPDF
import os
from datetime import datetime

def generate_initial_report(logics, output_path):
    # P = Portrait, mm = millimeters, A4
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Ancho efectivo (Margen de 10mm a cada lado)
    eff_width = pdf.w - 20 

    # --- Header ---
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(eff_width, 10, f"Logical Audit: {logics.get('contract_name', 'Unnamed')}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(eff_width, 8, f"Source file: {logics.get('source_file', 'Unnamed')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(eff_width, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # --- 1. Variables Inventory ---
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(eff_width, 10, "1. VARIABLE INVENTORY", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    i = 1
    for var in logics.get('variables', []):
        pdf.set_font("Helvetica", 'B', 10)
        pdf.write(5, f"{i}. {var['name']}: ")
        pdf.set_font("Helvetica", size=10)
        # Se asume que las keys ahora coinciden con tu JSON actualizado (page)
        pdf.write(5, f"{var.get('definition', '')}. Page: {var.get('definition_page', 'N/A')}.\n")
        i = i + 1
    
    pdf.ln(10)

    # --- 2. Logical Rules & Evidence ---
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(eff_width, 10, "2. LOGICAL RULES & EVIDENCE", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    for cond in logics.get('logical_conditions', []):
        # Rule ID
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(eff_width, 8, f"Rule {cond['id']}:", new_x="LMARGIN", new_y="NEXT")
        
        # Bloque de Fórmula (Gris)
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(eff_width, 8, f"  {cond['formula']}  ", border=0, fill=True, align='L', new_x="LMARGIN", new_y="NEXT")
        
        # Bloque de Evidencia (Debajo de la fórmula)
        pdf.set_font("Helvetica", 'I', 9)
        pdf.set_text_color(100, 100, 100)
        evidence_text = f"Source (Page {cond.get('evidence_page', 'N/A')}): {cond['evidence']}"
        pdf.multi_cell(eff_width, 5, evidence_text, align='L', new_x="LMARGIN", new_y="NEXT")
        
        # Reset color y espacio entre reglas
        pdf.set_text_color(0, 0, 0)
        pdf.ln(8)

    # Crear carpeta si no existe y guardar
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    pdf.output(output_path)

def generate_final_report(z3_result, logics, cfo_data, output_path):
    # P = Portrait, mm = millimeters, A4
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Ancho efectivo
    eff_width = pdf.w - 20

    # --- Header ---
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(eff_width, 10, f"Formal verification: {logics.get('contract_name', 'Unnamed')}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(eff_width, 8, f"Source file: {logics.get('source_file', 'Unnamed')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(eff_width, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # 2. BLOQUE DEL VEREDICTO
    is_compliant = z3_result.get('is_compliant', False)
    if is_compliant:
        status_text = "PASSED: COMPLIANT WITH ALL COVENANTS"
        bg_color = (230, 255, 230)
        text_color = (0, 100, 0)
    else:
        status_text = "FAILED: COVENANT BREACH DETECTED"
        bg_color = (255, 230, 230)
        text_color = (150, 0, 0)

    pdf.set_fill_color(*bg_color)
    pdf.set_text_color(*text_color)
    pdf.set_font('Helvetica', 'B', 14)
    # Cambio: ln=1 -> new_x="LMARGIN", new_y="NEXT"
    pdf.cell(eff_width, 15, f"  {status_text}", border=1, align='L', fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # 3. TABLA DE VARIABLES
    pdf.set_text_color(0)
    pdf.set_font('Helvetica', 'B', 12)
    # Cambio: ln=1 -> new_x="LMARGIN", new_y="NEXT"
    pdf.cell(eff_width, 10, "Calculated Model Values:", border=0, new_x="LMARGIN", new_y="NEXT")
    
    # Columnas
    c1, c2, c3 = 85, 45, 40
    
    # Cabecera
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    # Cambio: ln=0 -> new_x="RIGHT", new_y="TOP"
    pdf.cell(c1, 10, " Variable Name", 1, align='L', fill=True, new_x="RIGHT", new_y="TOP")
    pdf.cell(c2, 10, "Value", 1, align='C', fill=True, new_x="RIGHT", new_y="TOP")
    # Cambio: ln=1 -> new_x="LMARGIN", new_y="NEXT"
    pdf.cell(c3, 10, "Data Origin", 1, align='C', fill=True, new_x="LMARGIN", new_y="NEXT")

    # Datos
    calc_values = z3_result.get('calculated_values', {})
    pdf.set_font('Helvetica', '', 10)
    
    for var, val in calc_values.items():
        is_input = var in cfo_data
        origin = "CFO INPUT" if is_input else "Z3 DERIVED"
        
        if isinstance(val, (int, float)):
            val_str = f"{val:,.2f}"
        else:
            val_str = str(val)

        if not is_input:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(0, 0, 120)
        else:
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0)

        pdf.cell(c1, 8, f" {var}", 1, new_x="RIGHT", new_y="TOP")
        # Cambio: ln=0 -> new_x="RIGHT", new_y="TOP"
        pdf.cell(c2, 8, f" {val_str}", 1, align='R', new_x="RIGHT", new_y="TOP")
        pdf.set_font('Helvetica', '', 8)
        # Cambio: ln=1 -> new_x="LMARGIN", new_y="NEXT"
        pdf.cell(c3, 8, f"{origin}", 1, align='C', new_x="LMARGIN", new_y="NEXT")

    pdf.output(output_path)