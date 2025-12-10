# Módulo que crea el PDF
from fpdf import FPDF

class PDFGuia(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Guía Generada por IA', 0, 1, 'C')
        self.ln(10)

def generar_pdf(guia_completa, output_path):
    """Genera el PDF final con texto e imágenes."""
    print("📄 Maquetando PDF...")
    pdf = PDFGuia()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for i, paso in enumerate(guia_completa):
        # Título del paso
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f"{i+1}. {paso['titulo']} ({paso['timestamp']})", 0, 1)
        
        # Descripción
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 6, paso['descripcion'])
        pdf.ln(2)
        
        # Bloque de código (si existe)
        if paso.get('codigo'):
            pdf.set_font('Courier', '', 10)
            pdf.set_fill_color(240, 240, 240) # Gris claro
            # Limpiamos caracteres que puedan romper FPDF
            codigo = paso['codigo'].encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, codigo, fill=True)
            pdf.ln(2)
            
        # Imagen
        if os.path.exists(paso['img_path']):
            # Calculamos ancho para que quepa (max 180mm)
            pdf.image(paso['img_path'], w=170)
            pdf.ln(10) # Espacio después de la imagen
            
    pdf.output(output_path)
    print(f"✨ PDF generado exitosamente en: {output_path}")