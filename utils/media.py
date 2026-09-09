import asyncio
import os

async def safe_delete(file_path: str):
    """
    Hapus file media/thumbnail secara aman tanpa memblokir event loop.
    Dipakai setiap kali sebuah stream berhenti/diganti/selesai, supaya
    folder downloads/ tidak menumpuk file-file lama yang sudah tidak
    terpakai (sebelumnya file hasil download TIDAK PERNAH dihapus
    setelah selesai diputar, sehingga disk terus penuh seiring waktu).
    """
    if not file_path:
        return
    try:
        await asyncio.to_thread(os.remove, file_path)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Gagal menghapus file {file_path}: {e}")

async def get_duration(file_path: str) -> float:
    if not file_path or not os.path.exists(file_path): return 0.0
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await process.communicate()
        return float(stdout.decode().strip())
    except:
        return 0.0

async def get_thumbnail(file_path: str, duration: float) -> str:
    if not file_path or duration <= 0: return None
    out_path = f"{file_path}_thumb.jpg"
    mid_time = duration / 2
    try:
        cmd = ["ffmpeg", "-y", "-ss", str(mid_time), "-i", file_path, "-vframes", "1", "-q:v", "2", out_path]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await process.communicate()
        if os.path.exists(out_path): return out_path
    except:
        pass
    return None
