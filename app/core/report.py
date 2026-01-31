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
    pdf.cell(eff_width, 8, f"Audit ID: {logics.get('audit_id', 'Unnamed')}", new_x="LMARGIN", new_y="NEXT")
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
        evidence_text = f"Source (Page {cond.get('evidence_page', 'N/A')}): {cond['evidence']}."
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
    pdf.cell(eff_width, 8, f"Audit ID: {logics.get('audit_id', 'Unnamed')}", new_x="LMARGIN", new_y="NEXT")
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

def generate_portfolio_report(portfolio, analysis_config, output_path="portfolio_executive_summary.pdf"):
    pdf = FPDF(orientation='L') 
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(30, 50, 100)
    pdf.cell(0, 15, "PORTFOLIO COMPLIANCE DASHBOARD", ln=True, align="C")
    pdf.ln(5)

    for client_id, deal in portfolio.items():
        # Fondo gris para el cliente
        pdf.set_fill_color(230, 230, 230)
        pdf.set_text_color(0)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f" Client: {client_id}", ln=True, fill=True, border="B")
        pdf.ln(2)

        col_year, col_q, row_h = 25, 62, 12
        pdf.set_font("Arial", "B", 10)
        pdf.cell(col_year, row_h, "Year", border=1, align="C")
        for q in ["Q1", "Q2", "Q3", "Q4"]:
            pdf.cell(col_q, row_h, q, border=1, align="C")
        pdf.ln()

        config = analysis_config.get(client_id, [])
        var_main = config[0] if len(config) > 0 else None
        var_opt = config[1] if len(config) > 1 else None

        for year in sorted(deal.history.keys()):
            pdf.set_font("Arial", "B", 10)
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
                    
                    display = f"PASS |"
                    if m1: display += f" ({m1})"
                    if m2: display += f" | ({m2})"
                    display += "."
                else:
                    # CASO BREACH: Solo el texto, sin métricas
                    pdf.set_text_color(200, 30, 30) # Rojo
                    display = "BREACH"

                pdf.set_font("Arial", "B", 9)
                pdf.cell(col_q, row_h, display, border=1, align="C")
                pdf.set_text_color(0) 

            pdf.ln()

        # Leyenda
        pdf.set_font("Arial", "I", 8)
        pdf.set_text_color(100)
        legend_text = f"* Metrics displayed (on PASS): (1) {var_main}" + (f"  (2) {var_opt}" if var_opt else "")
        pdf.cell(0, 8, legend_text, ln=True)
        pdf.ln(8)

    pdf.output(output_path)

def generate_stress_report(stress_results, output_path="portfolio_stress_summary.pdf"):
    pdf = FPDF(orientation='L') 
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Título con un toque "Corporate Risk"
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(100, 30, 30) 
    pdf.cell(0, 15, f"STRATEGIC STRESS TEST ({list(stress_results.values())[0]["year_quarter"]})", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0)
    target_var_name = next(iter(stress_results.values()))["target_var"]
    pdf.cell(0, 10, f"Stress target variable: {target_var_name}.", ln=True, align="L")
    pdf.ln(5)

    # Definimos columnas para las 4 métricas (incluyendo el Current Value)
    # Ancho total en Landscape es ~280mm útiles
    col_metric, row_h = 65, 12

    for client_id, analysis in stress_results.items():
        # Header del Cliente
        pdf.set_fill_color(235, 235, 235)
        pdf.set_text_color(0)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, f"Client: {client_id}.", ln=True, fill=True, border="B")
        pdf.ln(2)

        # Cabecera de la tabla
        pdf.set_font("Arial", "B", 9)
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(col_metric, row_h, "Current Value", border=1, align="C", fill=True)
        pdf.cell(col_metric, row_h, "Headroom (%)", border=1, align="C", fill=True)
        pdf.cell(col_metric, row_h, "Covenant Break Value", border=1, align="C", fill=True)
        pdf.cell(col_metric, row_h, "Risk Status", border=1, align="C", fill=True)
        pdf.ln()

        # Fila de Datos
        pdf.set_font("Arial", "", 10)
        
        # 1. Valor Actual
        pdf.cell(col_metric, row_h, f"{analysis['current_value']:,.2f}", border=1, align="C")

        # 2. Headroom %
        pdf.cell(col_metric, row_h, analysis["headroom_pct"], border=1, align="C")

        # 3. Valor de Ruptura
        pdf.cell(col_metric, row_h, f"{analysis['limit_value']:,.2f}", border=1, align="C")

        # 4. Status con semáforo
        status = analysis["status"]
        if status == "Safe":
            pdf.set_text_color(34, 139, 34) # Verde Bosque
        else:
            pdf.set_text_color(200, 30, 30) # Rojo Alerta

        pdf.set_font("Arial", "B", 10)
        pdf.cell(col_metric, row_h, status.upper(), border=1, align="C")
        
        # Reset para el siguiente bloque
        pdf.set_text_color(0)
        pdf.ln(18) 

    # Footer con metadata del análisis
    pdf.set_y(-20)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(150)
    pdf.cell(0, 5, "Note: Analysis performed via automated SMT (Satisfiability Modulo Theories) verification of credit agreement logical clauses.", align="R")

    pdf.output(output_path)

def generate_matrix_report(matrix_results, output_path="portfolio_sensitivity_matrix.pdf"):
    pdf = FPDF(orientation='L')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for client_id, data in matrix_results.items():
        pdf.add_page()
        meta = data["metadata"]
        grid = data["grid"] # La matriz de resultados
        
        # Título de la página
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 10, f"SENSITIVITY MATRIX: {client_id}", ln=True, align="C")
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, f"Stress Correlation: {meta['var_y'].upper()} (Y) vs {meta['var_x'].upper()} (X)", ln=True, align="C")
        pdf.ln(10)

        # Configuración de la tabla
        # En Landscape tenemos ~270mm. 
        cell_w = 35  # Ancho de cada celda de la matriz
        header_y_w = 45 # Ancho de la columna de etiquetas Y
        row_h = 12

        # --- CABECERA X (Etiqutas de la variable horizontal) ---
        pdf.set_font("Arial", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(header_y_w, row_h, f"Y: {meta['var_y']} \ X: {meta['var_x']}", border=1, align="C", fill=True)
        
        for label_x in meta["labels_x"]:
            pdf.cell(cell_w, row_h, label_x, border=1, align="C", fill=True)
        pdf.ln()

        # --- CUERPO DE LA MATRIZ (Filas) ---
        # Recorremos el grid. Cada 'row' en grid corresponde a un nivel de estrés de Y
        for i, row in enumerate(grid):
            # Etiqueta de la fila (Variable Y)
            pdf.set_font("Arial", "B", 9)
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
                
                pdf.set_font("Arial", "B", 8)
                pdf.cell(cell_w, row_h, txt, border=1, align="C", fill=True)
            
            pdf.set_text_color(0) # Reset color texto
            pdf.ln()

        # --- (Debajo del bucle de la matriz) ---

        # Añadir Resumen de Headroom de Alta Precisión
        pdf.ln(5)
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(40, 40, 40)
        
        # Recuperamos los nombres de las variables para el texto
        v_x = meta['var_x'].replace('_', ' ').title()
        v_y = meta['var_y'].replace('_', ' ').title()
        
        # Imprimimos los valores precisos almacenados en la raíz del diccionario
        pdf.cell(0, 8, f"Precise Headroom {v_x}: {data[f'headroom_x']}", ln=True)
        pdf.cell(0, 8, f"Precise Headroom {v_y}: {data[f'headroom_y']}", ln=True)

        # Leyenda explicativa al pie de la matriz (ya estaba en tu código)
        pdf.ln(5)
        pdf.set_font("Arial", "I", 9)

        # Leyenda explicativa al pie de la matriz
        pdf.ln(15)
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(100)
        pdf.multi_cell(0, 5, f"Legend: This matrix explores the combined impact of {meta['var_x']} and {meta['var_y']}. " 
                            f"Red cells ('BREACH') indicate a violation of one or more logical covenants in the credit agreement.")

    pdf.output(output_path)