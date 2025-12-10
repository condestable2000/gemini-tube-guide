# Módulo para descargar de YouTube
import os
import yt_dlp
import subprocess
import glob
import sys

def obtener_duracion(video_path):
    """Obtiene la duración del video en segundos usando ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', video_path
        ]
        # check=True lanzará error si ffprobe no está instalado
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout)
    except Exception as e:
        print(f"⚠️ Advertencia: No se pudo obtener duración (¿FFmpeg instalado?). Usando 10min por defecto. Error: {e}")
        return 600.0

def descargar_recursos(url, output_folder):
    print(f"⬇️  Procesando recurso: {url}")
    
    video_path = os.path.join(output_folder, "video.mp4")
    audio_path = os.path.join(output_folder, "audio.mp3")
    frames_folder = os.path.join(output_folder, "ia_frames")
    
    # Limpieza
    if os.path.exists(video_path): os.remove(video_path)
    if os.path.exists(audio_path): os.remove(audio_path)
    if not os.path.exists(frames_folder): os.makedirs(frames_folder)
    
    # Limpiar frames viejos
    for f in glob.glob(f"{frames_folder}/*.jpg"): os.remove(f)

    # 1. Descargar Video
    print("   Descargando vídeo...")
    ydl_opts = {
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720][ext=mp4]',
        'outtmpl': video_path,
        'quiet': True, 
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"❌ Error descargando video: {e}")
        sys.exit(1)
    
    # 2. Calcular Muestreo Dinámico
    duracion = obtener_duracion(video_path)
    MAX_IMAGENES = 700 
    INTERVALO_DESEADO = 2.0
    
    if (duracion / INTERVALO_DESEADO) > MAX_IMAGENES:
        intervalo_final = duracion / MAX_IMAGENES
        print(f"⚠️ Video largo. Ajustando a 1 foto cada {intervalo_final:.1f}s.")
    else:
        intervalo_final = INTERVALO_DESEADO
        print(f"✅ Video corto. Usando máxima densidad (1 foto cada {intervalo_final}s).")

    print("🎥 Generando recursos para la IA...")
    
    # 3. Extraer Audio (MODIFICADO: Sin forzar códec libmp3lame y mostrando errores)
    print("   Extrayendo audio...")
    try:
        cmd_audio = [
            'ffmpeg', '-i', video_path, 
            '-vn',           # No video
            '-b:a', '32k',   # Bitrate bajo
            audio_path, 
            '-y'             # Sobrescribir
        ]
        # Eliminamos stderr=subprocess.DEVNULL para ver el error si falla
        subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("\n❌ Error Crítico: FFmpeg falló al extraer el audio.")
        print("   Asegúrate de haber hecho 'Rebuild Container' en VS Code.")
        print(f"   Código de error: {e}")
        sys.exit(1)
    
    # 4. Extraer Capturas
    print("   Extrayendo capturas...")
    try:
        cmd_frames = [
            'ffmpeg', '-i', video_path, 
            '-vf', f'fps=1/{intervalo_final}', 
            '-q:v', '2', 
            f'{frames_folder}/frame_%03d.jpg', '-y'
        ]
        subprocess.run(cmd_frames, check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("❌ Error extrayendo imágenes.")
        sys.exit(1)
    
    return video_path, audio_path, frames_folder