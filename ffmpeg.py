# import subprocess
# import shlex

# # File paths
# video_file_path = "downloads/Bediüzzaman'dan Mektup Var - Rusya Esaretindeki O Hadiseye Dair ｜ 51.Бölüm.mp4"
# subtitle_file_path = "downloads/Bediüzzaman'dan Mektup Var - Rusya Esaretindeki O Hadiseye Dair ｜ 51.Бölüm.srt"
# output_file_path = "downloads/Bediüzzaman'dan Mektup Var - Rusya Esaretindeki O Hadiseye Dair ｜ 51.Бölüm_with_subtitles.mp4"

# # FFmpeg command
# command = [
#     "ffmpeg",
#     "-i", video_file_path,
#     "-vf", f"subtitles={subtitle_file_path}:charenc=UTF-8",
#     "-c:a", "copy",
#     output_file_path
# ]

# # Run the command
# try:
#     result = subprocess.run(
#         command,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#         check=True  # Raises CalledProcessError if FFmpeg fails
#     )
#     print("FFmpeg executed successfully.")
#     print("Output:", result.stdout)
# except subprocess.CalledProcessError as e:
#     print("FFmpeg failed!")
#     print("Error Output:", e.stderr)


# import os

# video_file_path = "downloads/Bediüzzaman'dan Mektup Var - Rusya Esaretindeki O Hadiseye Dair ｜ 51.Бölüm.mp4"
# print(f"File exists: {os.path.isfile(video_file_path)}")




import subprocess

def add_subtitles(input_video, input_subtitles, output_video, embed=False):
    """
    
    :param input_video: Путь к входному MP4 файлу
    :param input_subtitles: Путь к SRT-файлу
    :param output_video: Путь к выходному MP4 файлу
    :param embed: Если True, субтитры будут встраиваться в видео, иначе — прикрепляться как soft subtitles
    """

    input_video = "downloads/Qjwikgqic6A.mp4"
    input_subtitles = "downloads/Qjwikgqic6A.srt"
    output_video = "downloads/Qjwikgqic6A_with_subtitles.mp4"

    try:
        if embed:
            command = [
                "ffmpeg",
                "-i", input_video,
                "-vf", f"subtitles={input_subtitles}",
                "-c:a", "copy",
                output_video
            ]
        else:
            # Добавление субтитров как soft subtitles
            command = [
                "ffmpeg",
                "-i", input_video,
                "-i", input_subtitles,
                "-c", "copy",
                "-c:s", "mov_text",
                output_video
            ]
        
        subprocess.run(command, check=True)
        print(f"Субтитры успешно добавлены в {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при добавлении субтитров: {e}")
    except FileNotFoundError:
        print("Убедитесь, что ffmpeg установлен и доступен в PATH.")

# Пример использования
input_video_path = "input.mp4"
input_srt_path = "input.srt"
output_video_path = "output.mp4"

# Встраивание субтитров
add_subtitles(input_video_path, input_srt_path, output_video_path, embed=True)

# Добавление как soft subtitles
# add_subtitles(input_video_path, input_srt_path, output_video_path, embed=False)
