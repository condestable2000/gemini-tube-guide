# Módulo para descargar de YouTube
import os
import yt_dlp
import subprocess
import glob
import sys
from dotenv import load_dotenv

# Cargar variables por si se ejecuta este script directamente
load_dotenv()

def obtener_duracion(video_path):
    """Obtiene la duración del video en segundos usando ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', video_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout)
    except Exception as e:
        print(f"⚠️  Advertencia: No se pudo obtener duración. Usando 10min por defecto.")
        return 600.0

def descargar_recursos(url, output_folder):
    print(f"⬇️  Procesando recurso: {url}")
    
    base_filename = os.path.join(output_folder, "video")
    video_path = os.path.join(output_folder, "video.mp4")
    audio_path = os.path.join(output_folder, "audio.mp3")
    frames_folder = os.path.join(output_folder, "ia_frames")
    
    # Limpieza previa
    if os.path.exists(video_path): os.remove(video_path)
    if os.path.exists(audio_path): os.remove(audio_path)
    if not os.path.exists(frames_folder): os.makedirs(frames_folder)
    for f in glob.glob(f"{frames_folder}/*.jpg"): os.remove(f)

    # 1. Descargar Video
    print("   📡 Conectando con YouTube...")
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'merge_output_format': 'mp4',
        'outtmpl': base_filename,
        'quiet': False, 
        'no_warnings': False,
        'nocheckcertificate': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"\n❌ Error fatal en yt-dlp: {e}")
        sys.exit(1)
    
    # Verificación y renombrado si es necesario
    archivos_descargados = glob.glob(os.path.join(output_folder, "video.*"))
    if not archivos_descargados:
        print("❌ Error: yt-dlp no generó ningún archivo.")
        sys.exit(1)
    
    archivo_real = archivos_descargados[0]
    if archivo_real != video_path:
        if os.path.exists(video_path): os.remove(video_path)
        os.rename(archivo_real, video_path)

    # 2. Calcular Muestreo Dinámico (CON VALORES DEL .ENV)
    print("   ⏱️  Calculando duración y densidad de muestreo...")
    duracion = obtener_duracion(video_path)
    
    # --- AQUÍ ESTÁ EL CAMBIO ---
    # Leemos del entorno, con fallback a los valores originales si fallan
    try:
        MAX_IMAGENES = int(os.getenv("MAX_IMAGENES", "150"))
        INTERVALO_DESEADO = float(os.getenv("INTERVALO_DESEADO", "2.0"))
    except ValueError:
        print("⚠️ Error leyendo .env, usando valores por defecto (150 imgs, 2.0s)")
        MAX_IMAGENES = 150
        INTERVALO_DESEADO = 2.0
    
    # Lógica de cálculo
    if (duracion / INTERVALO_DESEADO) > MAX_IMAGENES:
        intervalo_final = duracion / MAX_IMAGENES
        print(f"      ℹ️ Video largo detectado.")
        print(f"      - Configuración .env: Máx {MAX_IMAGENES} imágenes.")
        print(f"      - Ajustando intervalo a: 1 foto cada {intervalo_final:.2f}s.")
    else:
        intervalo_final = INTERVALO_DESEADO
        print(f"      ✅ Video dentro de los límites.")
        print(f"      - Usando intervalo deseado (.env): 1 foto cada {intervalo_final}s.")

    print("🎥 Generando recursos para la IA...")
    
    # 3. Extraer Audio
    print("   🎵 Extrayendo audio...")
    try:
        cmd_audio = ['ffmpeg', '-i', video_path, '-vn', '-b:a', '32k', audio_path, '-y']
        subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error FFmpeg Audio: {e}")
        sys.exit(1)
    
    # 4. Extraer Capturas
    print("   📸 Extrayendo capturas...")
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
    
    return video_path, audio_path, frames_folder