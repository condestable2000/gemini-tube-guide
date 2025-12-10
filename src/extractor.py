# Módulo que usa FFmpeg para sacar fotos
import subprocess
import os

def capturar_frames(guia_json, video_path, output_folder):
    """Recorre el JSON y extrae una captura para cada paso usando FFmpeg."""
    print("📸 Extrayendo capturas de pantalla...")
    
    images_folder = os.path.join(output_folder, "images")
    os.makedirs(images_folder, exist_ok=True)
    
    for i, paso in enumerate(guia_json):
        timestamp = paso['timestamp']
        image_filename = f"step_{i+1}.jpg"
        image_path = os.path.join(images_folder, image_filename)
        
        # Comando FFmpeg para extraer 1 frame en alta calidad
        # -ss: salta al segundo, -i: input, -vframes 1: saca 1 foto
        cmd = [
            'ffmpeg', 
            '-ss', timestamp, 
            '-i', video_path, 
            '-vframes', '1', 
            '-q:v', '2', 
            image_path, 
            '-y' # Sobrescribir si existe
        ]
        
        # Ejecutamos en silencio
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Añadimos la ruta de la imagen al objeto JSON para usarla en el PDF
        paso['img_path'] = image_path
        print(f"   Frame capturado: {timestamp} -> {image_filename}")
        
    return guia_json