# Módulo que usa FFmpeg para sacar fotos
import subprocess
import os

def capturar_frames(guia_json, video_path, output_folder):
    print("📸 Extrayendo capturas finales de alta resolución...")
    
    images_folder = os.path.join(output_folder, "final_images")
    os.makedirs(images_folder, exist_ok=True)
    
    for i, paso in enumerate(guia_json):
        timestamp = paso['timestamp']
        image_filename = f"step_{i+1}.jpg"
        image_path = os.path.join(images_folder, image_filename)
        
        # Extraemos 1 frame en alta calidad en el segundo exacto
        cmd = [
            'ffmpeg', '-ss', timestamp, '-i', video_path, 
            '-frames:v', '1', '-q:v', '2', image_path, '-y'
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        paso['img_path'] = image_path
        print(f"   [{timestamp}] -> {image_filename}")
        
    return guia_json