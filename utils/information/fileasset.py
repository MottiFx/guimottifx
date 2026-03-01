# file information

import ffmpeg
from PIL import Image

def get_information_video(path) -> dict[str,any]:
    probe = ffmpeg.probe(path)
    video_info = {}

    for stream in probe["streams"]:
        if stream["codec_type"] == "video":  # Check if the stream is a video stream
            video_info = {
                "codec": stream.get("codec_name", "N/A"),
                "width": stream.get("width", "N/A"),
                "height": stream.get("height", "N/A"),
                "fps": format(float(eval(stream.get("avg_frame_rate", "0"))),".2f"),
                "bitrate": stream.get("bit_rate", "N/A"),
                "duration": format(float(stream.get("duration", "0.0")),".2f")
            }
            break  # Exit the loop after finding the first video stream

    return video_info

def get_information_image(path) -> dict[str,any]:
    with Image.open(path) as img:
        return {
            "format": img.format,
            "width": img.size[0],
            "height": img.size[1],
            "mode": img.mode
        }
    

def get_information_audio(path) -> dict[str,any]:
    probe = ffmpeg.probe(path)
    audio_info = {}
    
    for stream in probe["streams"]:
        if stream["codec_type"] == "audio":
            audio_info = {
                "codec": stream.get("codec_name", "N/A"),
                "bitrate": stream.get("bit_rate", "N/A"),
                "samplerate": stream.get("sample_rate", "N/A"),
                "channels": stream.get("channels", "N/A"),
                "duration": format(float(stream.get("duration", "0.0")),".2f")
            }
            break

    return audio_info
    
