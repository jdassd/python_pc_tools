from moviepy import VideoFileClip

def convert_video_format(input_path, output_path, codec):
    """Converts a video to a different format."""
    try:
        video_clip = VideoFileClip(input_path)
        video_clip.write_videofile(output_path, codec=codec)
        return f"Successfully converted {input_path} to {output_path}"
    except Exception as e:
        return f"Error converting video: {e}"

def cut_video(input_path, output_path, start_time, end_time):
    """Cuts a portion of a video file."""
    try:
        with VideoFileClip(input_path) as video:
            new_clip = video.subclip(start_time, end_time)
            new_clip.write_videofile(output_path)
        return f"Successfully cut video from {start_time}s to {end_time}s"
    except Exception as e:
        return f"Error cutting video: {e}"

def compress_video(input_path, output_path, bitrate):
    """Compresses a video by lowering its bitrate."""
    try:
        video_clip = VideoFileClip(input_path)
        video_clip.write_videofile(output_path, bitrate=bitrate)
        return f"Successfully compressed {input_path} with bitrate {bitrate}"
    except Exception as e:
        return f"Error compressing video: {e}"