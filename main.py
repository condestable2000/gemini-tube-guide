# Archivo principal que ejecuta todo
import os
from dotenv import load_dotenv
from src.downloader import descargar_video
from src.analyzer import analizar_con_gemini # Nota: ahora recibe audio_path
from src.extractor import capturar_frames
from src.generator import generar_pdf

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def main():
    if not API_KEY:
        print("❌ Error: Falta la API KEY en .env")
        return

    youtube_url = input("Introduce la URL de YouTube: ")
    base_output = "output"
    os.makedirs(base_output, exist_ok=True)
    
    try:
        # 1. Descargar (obtenemos video Y audio por separado)
        video_path, audio_path = descargar_video(youtube_url, base_output)
        
        # 2. Analizar (usamos el AUDIO, ahorrando 99% de cuota)
        guia_data = analizar_con_gemini(audio_path, API_KEY)
        
        # 3. Extraer capturas (usamos el VIDEO local con los tiempos que dio la IA)
        guia_con_fotos = capturar_frames(guia_data, video_path, base_output)
        
        # 4. Generar PDF
        generar_pdf(guia_con_fotos, os.path.join(base_output, "Guia_Final.pdf"))
        
    except Exception as e:
        print(f"\n❌ Fallo crítico: {e}")

if __name__ == "__main__":
    main()