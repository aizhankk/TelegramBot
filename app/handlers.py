from aiogram import types
from aiogram.types import FSInputFile
import whisper
from aiogram import types
from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from bot_instance import bot
import os, subprocess
from app.middlewares import TestMiddleware
import requests
router = Router()

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
  waiting_for_video_file = State()
  waiting_for_video = State()


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
    
    audio_file = os.path.join("Easy Turkish Dialogs For Beginners.mp3")
    try:
        await bot.send_audio(chat_id=message.chat.id, audio=FSInputFile(audio_file))
    except FileNotFoundError:
        await message.answer("Аудиофайл не найден.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при отправке аудио: {str(e)}")


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




@router.message(F.text == "Скачать видео с Youtube")
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
                await bot.send_video(chat_id=message.chat.id, video=types.FSInputFile(file_path))
                os.remove(file_path)
                break

        await message.reply("Готово!")
    except Exception as e:
        await message.reply(f"Произошла ошибка при загрузке: {str(e)}")
    await state.clear()







@router.message(F.text == "Скачать Youtube видео как аудио")
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
                        await bot.send_audio(chat_id=message.chat.id, audio=FSInputFile(audio_file_path))

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
                    await bot.send_document(chat_id=message.chat.id, document=FSInputFile(subtitle_path))
                    
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






@router.message(lambda message: message.text == "Добавить субтитры к Youtube видео")
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

    video_output_template = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")

    try:
        subprocess.run(
            ["yt-dlp", "-f", "best", "-o", video_output_template, url],
            check=True
        )
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        video_file_path = None
        for file in downloaded_files:
            if file.endswith((".mp4", ".webm")):
                video_file_path = os.path.join(DOWNLOAD_DIR, file)
                break
        
        if not video_file_path:
            await message.reply("Видео не найдено.")
            return

        await message.reply("Генерация субтитров, это может занять несколько минут...")
        model = whisper.load_model("base")
        result = model.transcribe(video_file_path, fp16=False)

        subtitle_path = os.path.splitext(video_file_path)[0] + ".srt"
        with open(subtitle_path, "w", encoding="utf-8-sig") as srt_file:
            for segment in result['segments']:
                start = segment['start']
                end = segment['end']
                text = segment['text']
                srt_file.write(f"{segment['id'] + 1}\n")
                srt_file.write(f"{format_time(start)} --> {format_time(end)}\n")
                srt_file.write(f"{text}\n\n")
        output_video_path = os.path.splitext(video_file_path)[0] + "_with_subtitles.mp4"

        try:
            normalized_subtitle_path = subtitle_path.replace("\\", "/")
            normalized_video_path = video_file_path.replace("\\", "/")
            normalized_output_path = output_video_path.replace("\\", "/")

            if not os.path.isfile(normalized_subtitle_path):
                raise FileNotFoundError(f"SRT файл не найден: {normalized_subtitle_path}")

            subprocess.run([
                "ffmpeg",
                "-i", normalized_video_path,
                "-vf", f"subtitles={normalized_subtitle_path}",
                "-c:a", "copy",
                normalized_output_path
            ], check=True)
            print("Видео успешно обработано.")
        except FileNotFoundError as e:
            print(f"Ошибка: {e}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка FFmpeg: {e}")


        if os.path.isfile(output_video_path):
            await message.reply("Субтитры добавлены, отправляем видео...")
            await bot.send_video(chat_id=message.chat.id, video=FSInputFile(output_video_path))

            os.remove(output_video_path)
            os.remove(video_file_path)
            os.remove(subtitle_path)
        else:
            await message.reply("Не удалось создать видео с субтитрами.")

    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}")

    finally:
        await state.clear()

def format_time(seconds: float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"




@router.message(F.text == "Конвертировать видео в аудио")
async def start_video_conversion(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте видеофайл, который вы хотите конвертировать в аудио.")
    await state.set_state(Reg.waiting_for_video_file)

@router.message(Reg.waiting_for_video_file)
async def video_to_audio(message: Message, state: FSMContext):
    if not message.video:
        await message.reply("Пожалуйста, отправьте корректный видеофайл.")
        return
    await message.reply("Видео получено! Конвертируем в аудио, подождите немного...")
    video_file_path = os.path.join(DOWNLOAD_DIR, f"{message.video.file_id}.mp4")
    audio_file_path = os.path.splitext(video_file_path)[0] + ".mp3"

    try:
        file_info = await bot.get_file(message.video.file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        response = requests.get(file_url)
        with open(video_file_path, "wb") as file:
            file.write(response.content)

        try:
            subprocess.run(
                ["ffmpeg", "-i", video_file_path, "-q:a", "0", "-map", "a", audio_file_path],
                check=True
            )

            if os.path.isfile(audio_file_path):
                await message.reply("Аудио готово, отправляем...")
                await bot.send_audio(chat_id=message.chat.id, audio=FSInputFile(audio_file_path))

                os.remove(audio_file_path)

        except subprocess.CalledProcessError as e:
            await message.reply(f"Ошибка при конвертации видео в аудио: {str(e)}")
        os.remove(video_file_path)
    except Exception as e:
        await message.reply(f"Произошла ошибка при обработке: {str(e)}")

    await state.clear()






from aiogram.types import ContentType

@router.message(lambda message: message.text == "Добавить субтитры к видео")
async def add_subtitles_to_video(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте видео, к которому нужно добавить субтитры.")
    await state.set_state(Reg.waiting_for_video)

@router.message(Reg.waiting_for_video)
async def process_video_with_subtitles(message: Message, state: FSMContext):
    if message.content_type != ContentType.VIDEO:
        await message.reply("Пожалуйста, отправьте видео.")
        return

    video_file = message.video
    video_file_id = video_file.file_id

    file_info = await bot.get_file(video_file_id)
    video_file_path = os.path.join(DOWNLOAD_DIR, f"{video_file.file_id}.mp4")
    await bot.download_file(file_info.file_path, video_file_path)

    await message.reply("Видео загружается и обрабатывается, подождите немного...")

    try:
        await message.reply("Генерация субтитров, это может занять несколько минут...")
        model = whisper.load_model("base")
        result = model.transcribe(video_file_path, fp16=False)

        subtitle_path = os.path.splitext(video_file_path)[0] + ".srt"
        with open(subtitle_path, "w", encoding="utf-8-sig") as srt_file:
            for segment in result['segments']:
                start = segment['start']
                end = segment['end']
                text = segment['text']
                srt_file.write(f"{segment['id'] + 1}\n")
                srt_file.write(f"{format_time(start)} --> {format_time(end)}\n")
                srt_file.write(f"{text}\n\n")

        output_video_path = os.path.splitext(video_file_path)[0] + "_with_subtitles.mp4"
        try:
            normalized_subtitle_path = subtitle_path.replace("\\", "/")
            normalized_video_path = video_file_path.replace("\\", "/")
            normalized_output_path = output_video_path.replace("\\", "/")

            if not os.path.isfile(normalized_subtitle_path):
                raise FileNotFoundError(f"SRT файл не найден: {normalized_subtitle_path}")

            subprocess.run([
                "ffmpeg",
                "-i", normalized_video_path,
                "-vf", f"subtitles={normalized_subtitle_path}",
                "-c:a", "copy",
                normalized_output_path
            ], check=True)
            print("Видео успешно обработано.")
        except FileNotFoundError as e:
            print(f"Ошибка: {e}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка FFmpeg: {e}")

        if os.path.isfile(output_video_path):
            await message.reply("Субтитры добавлены, отправляем видео...")
            await bot.send_video(chat_id=message.chat.id, video=FSInputFile(output_video_path))

            os.remove(output_video_path)
            os.remove(video_file_path)
            os.remove(subtitle_path)
        else:
            await message.reply("Не удалось создать видео с субтитрами.")

    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}")
    finally:
        await state.clear()

def format_time(seconds: float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"