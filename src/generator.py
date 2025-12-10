from fpdf import FPDF
import os

class PDFGuia(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Guía Técnica Generada por IA', 0, 1, 'C')
        self.ln(5)

def generar_pdf(guia_completa, output_path):
    print("📄 Maquetando PDF...")
    pdf = PDFGuia()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for i, paso in enumerate(guia_completa):
        # Título
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"{i+1}. {paso['titulo']} ({paso['timestamp']})", 0, 1)
        
        # Descripción
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 6, paso['descripcion'])
        pdf.ln(2)
        
        # Código (con fondo gris)
        if paso.get('codigo'):
            pdf.set_font('Courier', '', 10)
            pdf.set_fill_color(245, 245, 245)
            pdf.set_text_color(50, 50, 50)
            # Saneamiento básico de caracteres
            codigo = paso['codigo'].encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, codigo, fill=True, border=0)
            pdf.ln(2)
            
        # Imagen
        if os.path.exists(paso['img_path']):
            pdf.image(paso['img_path'], w=170)
            pdf.ln(10)
            
    pdf.output(output_path)
    print(f"✨ PDF generado: {output_path}")