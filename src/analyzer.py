# Módulo que habla con Gemini
import google.generativeai as genai
import time
import json
import os
import glob
from PIL import Image

def analizar_con_gemini(audio_path, frames_folder, api_key):
    genai.configure(api_key=api_key)
    
    # Usamos el modelo Flash Lite (ideal para capa gratuita)
    # Si este nombre da error, usa: "models/gemini-2.0-flash-lite-preview-02-05"
    MODEL_NAME = "models/gemini-2.5-flash-lite"
    
    print(f"🧠 Cargando contexto multimodal en {MODEL_NAME}...")

    # 1. Subir Audio
    audio_file = genai.upload_file(path=audio_path)
    while audio_file.state.name == "PROCESSING":
        time.sleep(1)
        audio_file = genai.get_file(audio_file.name)

    # 2. Cargar Imágenes
    image_files = sorted(glob.glob(f"{frames_folder}/*.jpg"))
    images_payload = []
    
    # Límite duro de seguridad para no romper la petición (aunque Flash aguanta muchas)
    LIMIT_IMGS = 200
    if len(image_files) > LIMIT_IMGS:
        step = len(image_files) // LIMIT_IMGS
        image_files = image_files[::step]
    
    for img_path in image_files:
        images_payload.append(Image.open(img_path))
        
    print(f"   - Audio listo.")
    print(f"   - {len(images_payload)} Capturas cargadas para análisis visual.")

    # 3. Prompt Senior
    prompt = """
    Actúa como un Desarrollador Senior y Redactor Técnico.
    Estás analizando un video tutorial. Tienes el audio y capturas de pantalla secuenciales.
    
    TU OBJETIVO:
    Crear una guía técnica paso a paso EXTREMADAMENTE DETALLADA.
    
    INSTRUCCIONES:
    1. Escucha el audio para el contexto y mira las imágenes para extraer el CÓDIGO EXACTO.
    2. Si ves código en pantalla, transcríbelo en el campo 'codigo'.
    3. Determina el timestamp (MM:SS) donde empieza cada paso importante.
    4. Sé técnico: menciona archivos, puertos, comandos y configuraciones.
    
    Responde SOLO con este JSON:
    [
      {
        "titulo": "Título de la Acción",
        "descripcion": "Explicación técnica detallada...",
        "codigo": "npm install (o bloque de código)",
        "timestamp": "01:20"
      }
    ]
    """
    
    print("🤖 Generando análisis profundo...")
    model = genai.GenerativeModel(model_name=MODEL_NAME)
    
    try:
        response = model.generate_content(
            [prompt, audio_file] + images_payload,
            generation_config={"response_mime_type": "application/json"}
        )
        text_response = response.text.replace("```json", "").replace("```", "")
        return json.loads(text_response)

    except Exception as e:
        print(f"❌ Error en Gemini: {e}")
        raise e