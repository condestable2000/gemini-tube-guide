# Módulo que habla con Gemini
import google.generativeai as genai
import time
import json
import os

def analizar_con_gemini(audio_path, api_key):
    """Sube el AUDIO a Gemini (muy barato en tokens) y genera la guía."""
    print("🧠 Conectando con Gemini (Modo Audio)...")
    genai.configure(api_key=api_key)
    
    # Usamos Flash 1.5, es muy estable y rápido para audio
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    
    # 1. Subir solo el audio
    print(f"📤 Subiendo audio a la nube...")
    audio_file = genai.upload_file(path=audio_path)
    
    print("⏳ Procesando audio...")
    while audio_file.state.name == "PROCESSING":
        time.sleep(1)
        audio_file = genai.get_file(audio_file.name)
        
    if audio_file.state.name == "FAILED":
        raise ValueError("❌ El procesamiento del audio falló.")

    # 2. El Prompt ajustado para trabajar solo con audio
    prompt = """
    Escucha atentamente este tutorial técnico. Tu objetivo es crear una guía visual paso a paso.
    Aunque solo puedes oír, deduce cuándo ocurren las acciones importantes en la pantalla basándote en la explicación del narrador.
    
    TAREA:
    Genera un JSON con los pasos clave.
    Para el campo 'timestamp', estima el momento (MM:SS) donde el narrador empieza a explicar o realizar la acción.
    Si menciona comandos de código, inclúyelos.

    Responde ÚNICAMENTE con este JSON:
    [
      {
        "titulo": "Título del paso",
        "descripcion": "Resumen claro de la acción",
        "codigo": "comando si se menciona (o null)",
        "timestamp": "00:00"
      }
    ]
    """
    
    print("🤖 Generando estructura de la guía...")
    try:
        response = model.generate_content(
            [audio_file, prompt],
            generation_config={"response_mime_type": "application/json"}
        )
    except Exception as e:
        print(f"\n❌ Error de API: {e}")
        raise e
    
    text_response = response.text.replace("```json", "").replace("```", "")
    return json.loads(text_response)