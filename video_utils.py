def _ffmpeg_error_hint(e):
    msg = str(e).lower()
    if 'ffmpeg' in msg:
        return " 未检测到FFmpeg，请安装并将其添加到系统PATH后重试。"
    return ""


def _import_moviepy():
    try:
        from moviepy.editor import VideoFileClip  # noqa: WPS433
        return VideoFileClip
    except Exception as e:
        # 提示安装 moviepy 及 FFmpeg 绑定
        raise ImportError(f"MoviePy 未安装或导入失败：{e}。请先安装依赖：pip install moviepy imageio-ffmpeg")


def convert_video_format(input_path, output_path, codec):
    """Converts a video to a different format."""
    try:
        VideoFileClip = _import_moviepy()
        with VideoFileClip(input_path) as video_clip:
            video_clip.write_videofile(output_path, codec=codec)
        return f"Successfully converted {input_path} to {output_path}"
    except Exception as e:
        return f"Error converting video: {e}{_ffmpeg_error_hint(e)}"


def cut_video(input_path, output_path, start_time, end_time):
    """Cuts a portion of a video file."""
    try:
        if start_time is None or end_time is None or start_time < 0 or end_time <= start_time:
            return "Error cutting video: 无效的时间范围，确保起始时间小于结束时间且均为非负数。"
        VideoFileClip = _import_moviepy()
        with VideoFileClip(input_path) as video:
            duration = video.duration or 0
            if end_time > duration:
                end_time = duration
            new_clip = video.subclip(start_time, end_time)
            new_clip.write_videofile(output_path)
        return f"Successfully cut video from {start_time}s to {end_time}s"
    except Exception as e:
        return f"Error cutting video: {e}{_ffmpeg_error_hint(e)}"


def compress_video(input_path, output_path, bitrate):
    """Compresses a video by lowering its bitrate."""
    try:
        VideoFileClip = _import_moviepy()
        with VideoFileClip(input_path) as video_clip:
            video_clip.write_videofile(output_path, bitrate=bitrate)
        return f"Successfully compressed {input_path} with bitrate {bitrate}"
    except Exception as e:
        return f"Error compressing video: {e}{_ffmpeg_error_hint(e)}"