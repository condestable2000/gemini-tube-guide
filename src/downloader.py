# Módulo para descargar de YouTube
import os
import yt_dlp
import subprocess
import glob

def obtener_duracion(video_path):
    """Obtiene la duración del video en segundos usando ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
        '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(result.stdout)
    except:
        return 600.0 # 10 min por defecto si falla

def descargar_recursos(url, output_folder):
    """Descarga video y genera audio + capturas optimizadas para IA."""
    print(f"⬇️  Procesando recurso: {url}")
    
    video_path = os.path.join(output_folder, "video.mp4")
    audio_path = os.path.join(output_folder, "audio.mp3")
    frames_folder = os.path.join(output_folder, "ia_frames")
    
    # Limpieza
    if os.path.exists(video_path): os.remove(video_path)
    if os.path.exists(audio_path): os.remove(audio_path)
    if not os.path.exists(frames_folder): os.makedirs(frames_folder)
    files = glob.glob(f"{frames_folder}/*.jpg")
    for f in files: os.remove(f)

    # 1. Descargar Video (720p es suficiente para leer código)
    ydl_opts = {
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720][ext=mp4]',
        'outtmpl': video_path,
        'quiet': True, 'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # 2. Calcular Muestreo Dinámico
    duracion = obtener_duracion(video_path)
    
    # Queremos máximo detalle (1 foto cada 2s) pero con un tope de seguridad (150 fotos)
    MAX_IMAGENES = 700 
    INTERVALO_DESEADO = 2.0
    
    if (duracion / INTERVALO_DESEADO) > MAX_IMAGENES:
        intervalo_final = duracion / MAX_IMAGENES
        print(f"⚠️ Video largo. Ajustando a 1 foto cada {intervalo_final:.1f}s (Total ~150).")
    else:
        intervalo_final = INTERVALO_DESEADO
        print(f"✅ Video corto. Usando máxima densidad (1 foto cada {intervalo_final}s).")

    print("🎥 Generando recursos para la IA...")
    
    # 3. Extraer Audio (MP3 ligero 32k)
    subprocess.run([
        'ffmpeg', '-i', video_path, '-vn', '-acodec', 'libmp3lame', '-b:a', '32k', audio_path, '-y'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 4. Extraer Capturas (Slideshow para la IA)
    subprocess.run([
        'ffmpeg', '-i', video_path, 
        '-vf', f'fps=1/{intervalo_final}', 
        '-q:v', '2', 
        f'{frames_folder}/frame_%03d.jpg', '-y'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return video_path, audio_path, frames_folder