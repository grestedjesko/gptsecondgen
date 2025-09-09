import time
import tempfile
from io import BytesIO
from pydub import AudioSegment
from faster_whisper import WhisperModel
from aiogram import Bot
from aiogram.types import Message


class WhisperService:
    def __init__(self, model: WhisperModel):
        self.model = model

    async def transcribe_voice(self, message: Message, bot: Bot) -> tuple[str, float]:
        tg_file = await bot.get_file(message.voice.file_id)
        ogg_bytes = BytesIO()
        await bot.download_file(tg_file.file_path, ogg_bytes)
        ogg_bytes.seek(0)

        audio = AudioSegment.from_file(ogg_bytes, format="ogg")
        wav_bytes = BytesIO()
        audio.export(wav_bytes, format="wav")
        wav_bytes.seek(0)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav_bytes.read())
            tmp_path = tmp.name

        start_time = time.time()
        segments, _ = self.model.transcribe(
            audio=tmp_path,
            language="ru",
            beam_size=1,
            vad_filter=True
        )
        transcription_time = time.time() - start_time
        text = "".join([segment.text for segment in segments]).strip()

        return text
