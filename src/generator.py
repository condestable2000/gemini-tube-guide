from fpdf import FPDF
import os

class PDFGuia(FPDF):
    def __init__(self, titulo_video):
        super().__init__()
        self.titulo_video = titulo_video

    def header(self):
        self.set_font('Arial', 'B', 14)
        # Limpieza de caracteres para FPDF (Latin-1)
        safe_title = self.titulo_video.encode('latin-1', 'replace').decode('latin-1')
        
        # Usamos multi_cell por si el título es muy largo
        self.multi_cell(0, 10, safe_title, 0, 'C')
        self.ln(5)

    def footer(self):
        # Pie de página opcional con número
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_pdf(guia_completa, output_path, video_title):
    print("📄 Maquetando PDF...")
    
    # Pasamos el título al crear la instancia
    pdf = PDFGuia(video_title)
    
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for i, paso in enumerate(guia_completa):
        # Título del paso
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(0, 0, 0)
        
        titulo_paso = f"{i+1}. {paso['titulo']} ({paso['timestamp']})"
        safe_paso_title = titulo_paso.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.cell(0, 10, safe_paso_title, 0, 1)
        
        # Descripción
        pdf.set_font('Arial', '', 11)
        safe_desc = paso['descripcion'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, safe_desc)
        pdf.ln(2)
        
        # Código
        if paso.get('codigo'):
            pdf.set_font('Courier', '', 10)
            pdf.set_fill_color(245, 245, 245)
            pdf.set_text_color(50, 50, 50)
            
            safe_code = paso['codigo'].encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, safe_code, fill=True, border=0)
            pdf.ln(2)
            
        # Imagen
        if os.path.exists(paso['img_path']):
            # Ajustamos ancho para no salirnos
            pdf.image(paso['img_path'], w=170)
            pdf.ln(10)
            
    pdf.output(output_path)
    print(f"✨ PDF generado: {output_path}")