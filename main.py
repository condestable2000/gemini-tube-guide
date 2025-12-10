# Archivo principal que ejecuta todo
import os
import sys
from dotenv import load_dotenv
from src.downloader import descargar_recursos
from src.analyzer import analizar_con_gemini
from src.extractor import capturar_frames
from src.generator import generar_pdf

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def main():
    if not API_KEY:
        print("❌ Error: Falta GEMINI_API_KEY en .env")
        return

    if len(sys.argv) > 1:
        youtube_url = sys.argv[1]
    else:
        youtube_url = input("Introduce la URL de YouTube: ")
    
    base_output = "output"
    os.makedirs(base_output, exist_ok=True)
    
    try:
        # 1. Descarga (Ahora devuelve el Título también)
        video_path, audio_path, frames_folder, video_title = descargar_recursos(youtube_url, base_output)
        print(f"📘 Título detectado: {video_title}")
        
        # 2. Análisis IA
        guia_data = analizar_con_gemini(audio_path, frames_folder, API_KEY)
        
        # 3. Frames finales
        guia_con_fotos = capturar_frames(guia_data, video_path, base_output)
        
        # 4. Generar PDF (Pasando el título real)
        generar_pdf(guia_con_fotos, os.path.join(base_output, "Guia_Senior.pdf"), video_title)
        
    except Exception as e:
        print(f"\n❌ Proceso fallido: {e}")

if __name__ == "__main__":
    main()