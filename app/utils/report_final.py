from fpdf import FPDF
from datetime import datetime

def generate_final_report(z3_output, title, input_data, output_path="audit_FINAL.pdf"):

    # P = Portrait, mm = millimeters, A4
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Ancho efectivo (Margen de 10mm a cada lado)
    eff_width = pdf.w - 20

    # --- Header ---
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(eff_width, 10, f"Formal verification: {title}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(eff_width, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # 2. BLOQUE DEL VEREDICTO (Verde o Rojo)
    is_compliant = z3_output.get('is_compliant', False)
    if is_compliant:
        status_text = "PASSED: COMPLIANT WITH ALL COVENANTS"
        bg_color = (230, 255, 230)  # Verde muy claro
        text_color = (0, 100, 0)    # Verde oscuro
    else:
        status_text = "FAILED: COVENANT BREACH DETECTED"
        bg_color = (255, 230, 230)  # Rojo muy claro
        text_color = (150, 0, 0)    # Rojo oscuro

    pdf.set_fill_color(*bg_color)
    pdf.set_text_color(*text_color)
    pdf.set_font('Arial', 'B', 14)
    # Dibujamos una caja para el veredicto
    pdf.cell(eff_width, 15, f"  {status_text}", 1, 1, 'L', fill=True)
    pdf.ln(10)

    # 3. TABLA DE VARIABLES (Agnóstica)
    pdf.set_text_color(0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(eff_width, 10, "Calculated Model Values:", 0, 1)
    
    # Configuración de columnas
    c1, c2, c3 = 85, 45, 40
    
    # Cabecera
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(c1, 10, " Variable Name", 1, 0, 'L', True)
    pdf.cell(c2, 10, "Value", 1, 0, 'C', True)
    pdf.cell(c3, 10, "Data Origin", 1, 1, 'C', True)

    # Datos
    calc_values = z3_output.get('calculated_values', {})
    pdf.set_font('Arial', '', 10)
    
    for var, val in calc_values.items():
        # Lógica de origen
        is_input = var in input_data
        origin = "CFO INPUT" if is_input else "Z3 DERIVED"
        
        # Formateo de número (si es posible)
        if isinstance(val, (int, float)):
            val_str = f"{val:,.2f}"
        else:
            val_str = str(val)

        # Resaltar si es derivado por el motor
        if not is_input:
            pdf.set_font('Arial', 'B', 10)
            pdf.set_text_color(0, 0, 120) # Azul oscuro para lo que Z3 calculó
        else:
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(0)

        pdf.cell(c1, 8, f" {var}", 1)
        pdf.cell(c2, 8, f" {val_str}", 1, 0, 'R')
        pdf.set_font('Arial', '', 8) # Origen un poco más pequeño
        pdf.cell(c3, 8, f"{origin}", 1, 1, 'C')

    pdf.output(output_path)