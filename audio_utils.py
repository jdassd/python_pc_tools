from pydub import AudioSegment

def convert_audio_format(input_path, output_path, format):
    """Converts an audio file to a different format."""
    try:
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format=format)
        return f"Successfully converted {input_path} to {output_path}"
    except Exception as e:
        return f"Error converting audio: {e}"

def cut_audio(input_path, output_path, start_ms, end_ms):
    """Cuts a portion of an audio file."""
    try:
        audio = AudioSegment.from_file(input_path)
        cut_audio = audio[start_ms:end_ms]
        cut_audio.export(output_path, format=output_path.split('.')[-1])
        return f"Successfully cut audio from {start_ms}ms to {end_ms}ms"
    except Exception as e:
        return f"Error cutting audio: {e}"

def adjust_volume(input_path, output_path, db):
    """Adjusts the volume of an audio file."""
    try:
        audio = AudioSegment.from_file(input_path)
        adjusted_audio = audio + db
        adjusted_audio.export(output_path, format=output_path.split('.')[-1])
        return f"Successfully adjusted volume by {db}dB"
    except Exception as e:
        return f"Error adjusting volume: {e}"