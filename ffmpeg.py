# import assemblyai as aai

# aai.settings.api_key = ""
# transcript = aai.Transcriber().transcribe("downloads/Easy Turkish Dialogs For Beginners.mp4")
# sub = transcript.export_subtitles_srt()

# f = open("downloads/Easy Turkish Dialogs For Beginners.srt", "a")
# f.write(sub)
# f.close


import os
import subprocess

# Define input video file and subtitles file
video_file_path = "downloads/Easy Turkish Dialogs For Beginners.mp4"
subtitles_file_path = "downloads/Easy Turkish Dialogs For Beginners.srt"

# Define output video file
output_video_path = os.path.splitext(video_file_path)[0] + "_with_subtitles.mp4"

# Run the ffmpeg command
subprocess.run(
    [
        "ffmpeg", 
        "-i", video_file_path, 
        "-vf", f"subtitles={subtitles_file_path}", 
        "-c:a", "copy", 
        output_video_path
    ],
    check=True
)
