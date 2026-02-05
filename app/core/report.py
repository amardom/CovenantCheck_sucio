from fpdf import FPDF
import os

def generate_initial_report(logics, output_path):
    # P = Portrait, mm = millimeters, A4
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Ancho efectivo (Margen de 10mm a cada lado)
    eff_width = pdf.w - 20 

    # --- Header ---
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(eff_width, 10, f"Logical Audit", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(eff_width, 8, f"Contract: {logics.get('contract_name', 'Unnamed')}.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(eff_width, 8, f"Audit ID: {logics.get('audit_id', 'Unnamed')}.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # --- 1. Variables Inventory ---
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(eff_width, 10, "1. VARIABLE INVENTORY", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    
    i = 1
    for var in logics.get('variables', []):
        pdf.set_font("Helvetica", 'B', 10)
        pdf.write(5, f"{i}. {var['name']}: ")
        pdf.set_font("Helvetica", size=10)
        # Se asume que las keys ahora coinciden con tu JSON actualizado (page)
        pdf.write(5, f"{var.get('definition', '')}. Page: {var.get('definition_page', 'N/A')}.\n")
        i = i + 1
    
    pdf.ln(5)

    # --- 2. Logical Rules & Evidence ---
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(eff_width, 10, "2. LOGICAL RULES & EVIDENCE", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    
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
        evidence_text = f"Source (Page {cond.get('evidence_page', 'N/A')}): {cond['evidence']}."
        pdf.multi_cell(eff_width, 5, evidence_text, align='L', new_x="LMARGIN", new_y="NEXT")
        
        # Reset color y espacio entre reglas
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

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
    pdf.cell(eff_width, 10, f"Formal verification", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(eff_width, 8, f"Contract: {logics.get('contract_name', 'Unnamed')}.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(eff_width, 8, f"Audit ID: {logics.get('audit_id', 'Unnamed')}.", new_x="LMARGIN", new_y="NEXT")
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
    pdf.cell(eff_width, 15, f"  {status_text}", border=1, align='L', fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # 3. TABLA DE VARIABLES
    pdf.set_text_color(0)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(eff_width, 10, "Calculated Model Values:", border=0, new_x="LMARGIN", new_y="NEXT")
    
    # Columnas
    c1, c2, c3 = 85, 45, 40
    
    # Cabecera
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(c1, 10, " Variable Name", 1, align='L', fill=True, new_x="RIGHT", new_y="TOP")
    pdf.cell(c2, 10, "Value", 1, align='C', fill=True, new_x="RIGHT", new_y="TOP")
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
        pdf.cell(c2, 8, f" {val_str}", 1, align='R', new_x="RIGHT", new_y="TOP")
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(c3, 8, f"{origin}", 1, align='C', new_x="LMARGIN", new_y="NEXT")

    pdf.output(output_path)

def generate_portfolio_report(portfolio, analysis_config, output_path="portfolio_executive_summary.pdf"):
    # P = Portrait, mm = millimeters, A4
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Ancho efectivo
    eff_width = pdf.w - 20

    # --- Header ---
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(eff_width, 10, f"Portfolio compliance dashboard", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.ln(5)

    for client_id, deal in portfolio.items():
        # Fondo gris para el cliente
        pdf.set_fill_color(230, 230, 230)
        pdf.set_text_color(0)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, f" Client: {client_id}.", fill=True, border="B", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        col_year, col_q, row_h = 25, 41.25, 10
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(col_year, row_h, "Year", border=1, align="C")
        for q in ["Q1", "Q2", "Q3", "Q4"]:
            pdf.cell(col_q, row_h, q, border=1, align="C")
        pdf.ln()

        config = analysis_config.get(client_id, [])
        var_main = config[0] if len(config) > 0 else None
        var_opt = config[1] if len(config) > 1 else None

        for year in sorted(deal.history.keys()):
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(col_year, row_h, str(year), border=1, align="C")
            
            for q in ["Q1", "Q2", "Q3", "Q4"]:
                entry = deal.history[year].get(q)
                
                if not entry:
                    pdf.set_text_color(180)
                    pdf.cell(col_q, row_h, "-", border=1, align="C")
                    continue

                z3_res = entry.get("z3_result", {})
                is_ok = z3_res.get("is_compliant")
                
                # Solo buscamos métricas si el resultado es PASS
                if is_ok:
                    pdf.set_text_color(34, 139, 34) # Verde
                    
                    def get_metric(var_name):
                        if not var_name: return None
                        val = z3_res.get("calculated_values", {}).get(var_name)
                        if val is None:
                            val = entry.get("cfo_data", {}).get(var_name)
                        return f"{float(val):.2f}" if isinstance(val, (float, int)) else str(val)

                    m1 = get_metric(var_main)
                    m2 = get_metric(var_opt)
                    
                    display = f"OK |"
                    if m1: display += f" {m1}"
                    if m2: display += f" | {m2}"
                else:
                    # CASO BREACH: Solo el texto, sin métricas
                    pdf.set_text_color(200, 30, 30) # Rojo
                    display = "BREACH"

                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(col_q, row_h, display, border=1, align="C")
                pdf.set_text_color(0) 

            pdf.ln()

        # Leyenda
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100)
        legend_text = f"*Metrics displayed (on OK): (1) {var_main}" + (f" (2) {var_opt}." if var_opt else ".")
        pdf.cell(0, 8, legend_text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)

    pdf.output(output_path)

def generate_matrix_report(matrix_results, year, quarter, output_path="portfolio_sensitivity_matrix.pdf"):
    # P = Portrait, mm = millimeters, A4
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Ancho efectivo
    eff_width = pdf.w - 20

    # --- Header ---
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(eff_width, 10, f"Stress analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(eff_width, 8, f"Reporting period: {year}_{quarter}.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(7)
    
    for i, (client_id, data) in enumerate(matrix_results.items()):
        if i > 0: 
            pdf.add_page()
        meta = data["metadata"]
        grid = data["grid"] # La matriz de resultados
        
        # Fondo gris para el cliente
        pdf.set_fill_color(230, 230, 230)
        pdf.set_text_color(0)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, f" Client: {client_id}.", fill=True, border="B", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 10, f"Stress Correlation: {meta['var_y'].upper()} (Y) vs {meta['var_x'].upper()} (X).", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Configuración para A4 Portrait (Suma: 30 + 26.6*6 ≈ 190mm)
        header_y_w = 30  # Ancho columna etiquetas Y
        num_cols = len(meta["labels_x"])
        cell_w = (190 - header_y_w) / num_cols 
        row_h = 10

        # --- CABECERA X (Etiqutas de la variable horizontal) ---
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(header_y_w, row_h, f"Y \ X", border=1, align="C", fill=True)
        
        for label_x in meta["labels_x"]:
            pdf.cell(cell_w, row_h, label_x, border=1, align="C", fill=True)
        pdf.ln()

        # --- CUERPO DE LA MATRIZ (Filas) ---
        # Recorremos el grid. Cada 'row' en grid corresponde a un nivel de estrés de Y
        for i, row in enumerate(grid):
            # Etiqueta de la fila (Variable Y)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(header_y_w, row_h, meta["labels_y"][i], border=1, align="C", fill=True)
            
            # Celdas de resultado
            for cell in row:
                if cell["is_compliant"]:
                    pdf.set_fill_color(200, 255, 200) # Verde claro (PASS)
                    pdf.set_text_color(0, 100, 0)
                    txt = "OK"
                else:
                    pdf.set_fill_color(255, 200, 200) # Rojo claro (FAIL)
                    pdf.set_text_color(150, 0, 0)
                    txt = "BREACH"
                
                pdf.set_font("Helvetica", "B", 8)
                pdf.cell(cell_w, row_h, txt, border=1, align="C", fill=True)
            
            pdf.set_text_color(0) # Reset color texto
            pdf.ln()

        # Añadir Resumen de Headroom.
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(40, 40, 40)
        
        # Recuperamos los nombres de las variables para el texto
        v_x = meta['var_x'].replace('_', ' ').title()
        v_y = meta['var_y'].replace('_', ' ').title()
        
        # Imprimimos los valores precisos almacenados en la raíz del diccionario
        pdf.cell(0, 8, f"Headroom {v_x}: {data[f'headroom_x']}", ln=True)
        pdf.cell(0, 8, f"Headroom {v_y}: {data[f'headroom_y']}", ln=True)

        # Leyenda explicativa al pie de la matriz
        pdf.ln(5)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100)
        pdf.multi_cell(0, 5, f"This matrix explores the combined impact of {meta['var_x']} and {meta['var_y']}. " 
                            f"Red cells ('BREACH') indicate a violation of one or more logical covenants in the credit agreement.")

    pdf.output(output_path)