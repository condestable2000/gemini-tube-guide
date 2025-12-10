# Módulo para descargar de YouTube
import os
import yt_dlp
import subprocess
import glob
import sys
from dotenv import load_dotenv

load_dotenv()

def obtener_duracion(video_path):
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', video_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout)
    except Exception:
        return 600.0

def descargar_recursos(url, output_folder):
    print(f"⬇️  Procesando recurso: {url}")
    
    base_filename = os.path.join(output_folder, "video")
    video_path = os.path.join(output_folder, "video.mp4")
    audio_path = os.path.join(output_folder, "audio.mp3")
    frames_folder = os.path.join(output_folder, "ia_frames")
    
    if os.path.exists(video_path): os.remove(video_path)
    if os.path.exists(audio_path): os.remove(audio_path)
    if not os.path.exists(frames_folder): os.makedirs(frames_folder)
    for f in glob.glob(f"{frames_folder}/*.jpg"): os.remove(f)

    print("   📡 Conectando con YouTube...")
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'merge_output_format': 'mp4',
        'outtmpl': base_filename,
        'quiet': False, 
        'no_warnings': False,
        'nocheckcertificate': True,
    }
    
    video_title = "Guía Técnica" # Valor por defecto

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info descarga Y devuelve los metadatos
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', 'Guía Técnica')
            
    except Exception as e:
        print(f"\n❌ Error fatal en yt-dlp: {e}")
        sys.exit(1)
    
    # Renombrado seguro (igual que antes)
    archivos_descargados = glob.glob(os.path.join(output_folder, "video.*"))
    if archivos_descargados:
        archivo_real = archivos_descargados[0]
        if archivo_real != video_path:
            if os.path.exists(video_path): os.remove(video_path)
            os.rename(archivo_real, video_path)

    # Cálculo dinámico
    duracion = obtener_duracion(video_path)
    try:
        MAX_IMAGENES = int(os.getenv("MAX_IMAGENES", "150"))
        INTERVALO_DESEADO = float(os.getenv("INTERVALO_DESEADO", "2.0"))
    except ValueError:
        MAX_IMAGENES = 150
        INTERVALO_DESEADO = 2.0
    
    if (duracion / INTERVALO_DESEADO) > MAX_IMAGENES:
        intervalo_final = duracion / MAX_IMAGENES
    else:
        intervalo_final = INTERVALO_DESEADO

    print("🎥 Generando recursos para la IA...")
    
    # Audio
    try:
        cmd_audio = ['ffmpeg', '-i', video_path, '-vn', '-b:a', '32k', audio_path, '-y']
        subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("❌ Error extrayendo audio.")
        sys.exit(1)
    
    # Frames
    try:
        cmd_frames = [
            'ffmpeg', '-i', video_path, 
            '-vf', f'fps=1/{intervalo_final}', 
            '-q:v', '2', 
            f'{frames_folder}/frame_%03d.jpg', '-y'
        ]
        subprocess.run(cmd_frames, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("❌ Error extrayendo imágenes.")
        sys.exit(1)
    
    # ¡Ahora devolvemos también el título!
    return video_path, audio_path, frames_folder, video_title