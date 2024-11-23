from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from bot_instance import bot
import os
import subprocess
from aiogram import types
from aiogram.types import InputFile
import whisper

# middleware
from app.middlewares import TestMiddleware

router = Router()

# middleware
router.message.outer_middleware(TestMiddleware())

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

class Reg(StatesGroup):
  name = State()
  number = State()
  waiting_for_link = State()
  waiting_for_video_link = State()  
  waiting_for_audio_link = State()  
  waiting_for_subtitles_link = State() 

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(
        f'Hello!  \nТвой id: {message.from_user.id}\nИмя: {message.from_user.first_name}',
        reply_markup=kb.main
        # reply_markup =  await kb.inline_cars()
    )

@router.message(Command('help'))
async def get_help(message: Message):
  await message.answer('Это Команда /help')

@router.message(F.text == 'How are you?')
async def how_are_you(message: Message):
  await message.answer('OK!')

@router.message(Command('get_photo'))
async def get_help(message: Message):
  await message.answer_photo(photo='AgACAgIAAxkBAAMYZz5cMlFHrEuQNz4ij2mM5ZtEuwgAAq3tMRssafFJtQABEc-SSuJRAQADAgADeAADNgQ', 
                             caption='Это фото')
  
@router.message(F.photo)
async def get_photo(message: Message):
  await message.answer(f'ID photo: {message.photo[-1].file_id}')

@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
  await callback.answer('Вы выбрали каталог', show_alert=True)
  await callback.message.edit_text('Привет', reply_markup=await kb.inline_cars())

@router.message(Command('reg'))
async def reg_one(message: Message, state:FSMContext):
  await state.set_state(Reg.name)
  await message.answer('ВВедите ваше имя')

@router.message(Reg.name)
async def reg_two(message: Message, state: FSMContext):
  await state.update_data(name=message.text)
  await state.set_state(Reg.number)
  await message.answer('Введите номер телефона')

@router.message(Reg.number)
async def two_three(message: Message, state: FSMContext):
  await state.update_data(number=message.text)
  data = await state.get_data()
  await message.answer(f'Данные получены. \nName: {data["name"]}\nNumber: {data["number"]}')
  await state.clear()


@router.message(Command('download'))
async def start_download(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте ссылку на видео, которое вы хотите скачать.")
    await state.set_state(Reg.waiting_for_video_link)


@router.message(Reg.waiting_for_video_link)
async def process_video_link(message: Message, state: FSMContext):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.reply("Пожалуйста, введите корректную ссылку.")
        return

    await message.reply("Ссылка принята! Видео загружается, подождите немного...")
    output_path = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
    try:
        subprocess.run(
            ["yt-dlp", "-f", "best", "-o", output_path, url],
            check=True
        )
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        for file in downloaded_files:
            if file.endswith(".mp4") or file.endswith(".webm"):
                
                file_path = os.path.join(DOWNLOAD_DIR, file)
                print(f"File path: {file_path}")
                if not os.path.isfile(file_path):
                    await message.reply("Файл не найден.")
                    return
                await message.reply("Файл найден, отправляем...")
                await bot.send_video(chat_id=message.chat.id, video=types.InputFile(file_path))
                os.remove(file_path)
                break

        await message.reply("Готово!")
    except Exception as e:
        await message.reply(f"Произошла ошибка при загрузке: {str(e)}")
    await state.clear()







@router.message(Command('audio'))
async def start_download(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте ссылку на видео, которое вы хотите скачать как аудио.")
    await state.set_state(Reg.waiting_for_audio_link)

@router.message(Reg.waiting_for_audio_link)
async def video_to_audio(message: Message, state: FSMContext):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.reply("Пожалуйста, введите корректную ссылку.")
        return
    await message.reply("Ссылка принята! Видео загружается, подождите немного...")
    video_output_path = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
    try:
        # Download the video
        subprocess.run(
            ["yt-dlp", "-f", "best", "-o", video_output_path, url],
            check=True
        )
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        for file in downloaded_files:
            if file.endswith(".mp4") or file.endswith(".webm"):
                video_file_path = os.path.join(DOWNLOAD_DIR, file)
                print(f"Video file path: {video_file_path}")

                if not os.path.isfile(video_file_path):
                    await message.reply("Видео не найдено.")
                    return

                # Convert video to audio using ffmpeg
                audio_file_path = os.path.splitext(video_file_path)[0] + ".mp3"
                try:
                    subprocess.run(
                        ["ffmpeg", "-i", video_file_path, "-q:a", "0", "-map", "a", audio_file_path],
                        check=True
                    )
                    print(f"Audio file path: {audio_file_path}")

                    # Send the audio file to the user
                    if os.path.isfile(audio_file_path):
                        await message.reply("Аудио найдено, отправляем...")
                        await bot.send_audio(chat_id=message.chat.id, audio=InputFile(audio_file_path))

                        # Remove the audio file after sending
                        os.remove(audio_file_path)

                except subprocess.CalledProcessError as e:
                    await message.reply(f"Ошибка при конвертации видео в аудио: {str(e)}")

                # Remove the video file after processing
                os.remove(video_file_path)
                break

        await message.reply("Готово!")
    except Exception as e:
        await message.reply(f"Произошла ошибка при обработке: {str(e)}")

    await state.clear()






@router.message(Command('subtitles'))
async def generate_subtitles(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте ссылку на видео, для которого нужно сгенерировать субтитры.")
    await state.set_state(Reg.waiting_for_link)

@router.message(Reg.waiting_for_link)
async def process_subtitles(message: Message, state: FSMContext):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.reply("Пожалуйста, введите корректную ссылку.")
        return

    await message.reply("Ссылка принята! Видео загружается, подождите немного...")

    video_output_path = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
    
    try:
        subprocess.run(
            ["yt-dlp", "-f", "best", "-o", video_output_path, url],
            check=True
        )
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        for file in downloaded_files:
            if file.endswith(".mp4") or file.endswith(".webm"):
                video_file_path = os.path.join(DOWNLOAD_DIR, file)
                print(f"Video file path: {video_file_path}")

                if not os.path.isfile(video_file_path):
                    await message.reply("Видео не найдено.")
                    return

                await message.reply("Генерация субтитров, это может занять несколько минут...")
                model = whisper.load_model("base")
                result = model.transcribe(video_file_path, fp16=False)
                subtitle_path = os.path.splitext(video_file_path)[0] + ".srt"
                with open(subtitle_path, "w", encoding="utf-8") as srt_file:
                    for segment in result['segments']:
                        start = segment['start']
                        end = segment['end']
                        text = segment['text']
                        srt_file.write(f"{segment['id'] + 1}\n")
                        srt_file.write(f"{format_time(start)} --> {format_time(end)}\n")
                        srt_file.write(f"{text}\n\n")

                if os.path.isfile(subtitle_path):
                    await message.reply("Субтитры сгенерированы, отправляем...")
                    await bot.send_document(chat_id=message.chat.id, document=InputFile(subtitle_path))
                    
                    os.remove(subtitle_path)
                    os.remove(video_file_path)

                break
        await message.reply("Готово!")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}")

    await state.clear()

def format_time(seconds: float) -> str:
    """Convert time in seconds to SRT format (HH:MM:SS,ms)."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"






@router.message(Command('add_subtitles'))
async def add_subtitles_to_video(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте ссылку на видео, чтобы добавить субтитры.")
    await state.set_state(Reg.waiting_for_subtitles_link)

@router.message(Reg.waiting_for_subtitles_link)
async def process_video_with_subtitles(message: Message, state: FSMContext):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.reply("Пожалуйста, введите корректную ссылку.")
        return

    await message.reply("Видео загружается и обрабатывается, подождите немного...")

    video_output_path = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
    
    try:
        # Step 1: Download the video
        subprocess.run(
            ["yt-dlp", "-f", "best", "-o", video_output_path, url],
            check=True
        )

        # Locate the downloaded video
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        for file in downloaded_files:
            if file.endswith(".mp4") or file.endswith(".webm"):
                video_file_path = os.path.join(DOWNLOAD_DIR, file)

                if not os.path.isfile(video_file_path):
                    await message.reply("Видео не найдено.")
                    return

                # Step 2: Generate subtitles
                await message.reply("Генерация субтитров, это может занять несколько минут...")
                model = whisper.load_model("base")
                result = model.transcribe(video_file_path, fp16=False)
                subtitle_path = os.path.splitext(video_file_path)[0] + ".srt"

                with open(subtitle_path, "w", encoding="utf-8") as srt_file:
                    for segment in result['segments']:
                        start = segment['start']
                        end = segment['end']
                        text = segment['text']
                        srt_file.write(f"{segment['id'] + 1}\n")
                        srt_file.write(f"{format_time(start)} --> {format_time(end)}\n")
                        srt_file.write(f"{text}\n\n")

                # Step 3: Add subtitles to the video using FFmpeg
                output_video_path = os.path.splitext(video_file_path)[0] + "_with_subtitles.mp4"
                video_file_path = video_file_path.replace("\\", "/")
                subtitle_path = subtitle_path.replace("\\", "/")
                output_video_path = output_video_path.replace("\\", "/")
                try:
                    subprocess.run([
                        "ffmpeg",
                        "-i", video_file_path,
                        "-vf", f"subtitles={subtitle_path}",
                        "-c:a", "copy",
                        output_video_path
                    ], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"FFmpeg failed: {e}")
                    raise

                # Step 4: Send the video with subtitles
                if os.path.isfile(output_video_path):
                    await message.reply("Субтитры добавлены, отправляем видео...")
                    await bot.send_video(chat_id=message.chat.id, video=InputFile(output_video_path))
                    
                    # Cleanup
                    os.remove(output_video_path)
                    os.remove(video_file_path)
                    os.remove(subtitle_path)
                break
        await message.reply("Готово!")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}")

    await state.clear()

def format_time(seconds: float) -> str:
    """Convert time in seconds to SRT format (HH:MM:SS,ms)."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"


