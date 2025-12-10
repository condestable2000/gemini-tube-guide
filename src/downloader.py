# Módulo para descargar de YouTube
import os
import yt_dlp
import subprocess

def descargar_video(url, output_folder):
    """Descarga video para capturas y extrae audio para la IA."""
    print(f"⬇️ Procesando: {url}")
    
    video_filename = "video_temp.mp4"
    audio_filename = "audio_temp.mp3"
    
    video_path = os.path.join(output_folder, video_filename)
    audio_path = os.path.join(output_folder, audio_filename)
    
    # Limpieza previa
    if os.path.exists(video_path): os.remove(video_path)
    if os.path.exists(audio_path): os.remove(audio_path)

    # 1. Descargamos el video (Calidad media para que ocupe poco)
    ydl_opts = {
        'format': 'best[ext=mp4]', # No necesitamos 4k, pero sí que se vea bien el código
        'outtmpl': video_path,
        'quiet': True,
        'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    print("🎥 Video descargado. Extrayendo audio...")

    # 2. Extraemos el audio a MP3 usando FFmpeg (¡Esto es lo que enviaremos a la IA!)
    # -vn: no video, -acodec: codec de audio libmp3lame
    cmd = [
        'ffmpeg', '-i', video_path, 
        '-vn', '-acodec', 'libmp3lame', '-q:a', '4', 
        audio_path, '-y'
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("🎵 Audio extraído correctamente.")
    
    # Devolvemos ambas rutas
    return video_path, audio_path