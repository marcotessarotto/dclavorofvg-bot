import logging

# https://www.electricmonk.nl/log/2017/08/06/understanding-pythons-logging-module/

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

mainlogger = logging.getLogger('regionefvg_bot')  # "main" logger
mainlogger.setLevel(logging.INFO)

ormlogger = logging.getLogger('ormlayer')
ormlogger.setLevel(logging.DEBUG)

newslogger = ormlogger = logging.getLogger('news_processing')
newslogger.setLevel(logging.DEBUG)



