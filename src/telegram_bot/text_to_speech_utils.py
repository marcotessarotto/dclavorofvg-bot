from gtts import gTTS
import os

from src.backoffice.models import NewsItem, UI_news, TextToSpeechWordSubstitution
from src.gfvgbo.settings import AUDIO_ROOT

from src.telegram_bot.log_utils import main_logger as logger, benchmark_decorator

# Cloud Text-to-Speech API: Quotas & limits
# https://cloud.google.com/text-to-speech/quotas
TextToSpeechWordSubstitution.fill_substitutions()

# TODO: complete
TextToSpeechWordSubstitution.load()


@benchmark_decorator
def text_to_speech(news_item: NewsItem, text, lang='it'):

    str_id = str(news_item.id)

    work_dir = os.path.join(AUDIO_ROOT, str_id)

    fname = os.path.join(work_dir, f"{UI_news}_{str_id}.ogg")

    if os.path.isfile(fname) and os.path.getsize(fname) > 0:
        logger.info(f"text_to_speech: file exists, {fname}")
        return fname

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    text = "Notizia numero " + str_id + ". " + text

    tts = gTTS(text=text, lang=lang)

    tts.save(fname)

    logger.info(f"text_to_speech: file created, {fname}")

    return fname

    # TBD: text to speech of complete news item (title, categories, text)

