from pydub import AudioSegment
import os

def _ffmpeg_error_hint(e):
    msg = str(e).lower()
    if "ffmpeg" in msg or "couldn't find ffmpeg" in msg or "ffprobe" in msg:
        return " 未检测到FFmpeg，请安装并将其添加到系统PATH后重试。"
    return ""

def _ext_format_from_path(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    return ext if ext else "mp3"

def convert_audio_format(input_path, output_path, format):
    """Converts an audio file to a different format."""
    try:
        audio = AudioSegment.from_file(input_path)
        # 若未显式提供format，依据输出文件扩展名推断
        fmt = format or _ext_format_from_path(output_path)
        audio.export(output_path, format=fmt)
        return f"Successfully converted {input_path} to {output_path}"
    except Exception as e:
        return f"Error converting audio: {e}{_ffmpeg_error_hint(e)}"

def cut_audio(input_path, output_path, start_ms, end_ms):
    """Cuts a portion of an audio file."""
    try:
        if start_ms is None or end_ms is None or start_ms < 0 or end_ms <= start_ms:
            return "Error cutting audio: 无效的时间范围，确保起始时间小于结束时间且均为非负数。"
        audio = AudioSegment.from_file(input_path)
        duration = len(audio)  # 毫秒
        if end_ms > duration:
            end_ms = duration
        if start_ms >= duration:
            return "Error cutting audio: 起始时间超出音频长度。"
        segment = audio[start_ms:end_ms]
        fmt = _ext_format_from_path(output_path)
        segment.export(output_path, format=fmt)
        return f"Successfully cut audio from {start_ms}ms to {end_ms}ms"
    except Exception as e:
        return f"Error cutting audio: {e}{_ffmpeg_error_hint(e)}"

def adjust_volume(input_path, output_path, db):
    """Adjusts the volume of an audio file."""
    try:
        audio = AudioSegment.from_file(input_path)
        adjusted_audio = audio + db
        fmt = _ext_format_from_path(output_path)
        adjusted_audio.export(output_path, format=fmt)
        return f"Successfully adjusted volume by {db}dB"
    except Exception as e:
        return f"Error adjusting volume: {e}{_ffmpeg_error_hint(e)}"