
import shutil
import requests
import json
from boto3.resources.model import Request
import telegram
import os
import logging

from bot import plain_handler

OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps({'statusCode': 200})
}
ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps({'statusCode': 400})
}

logger = logging.getLogger()
if logger.handlers:
    for handle in logger.handlers:
        logger.removeHandler(handle)
logging.basicConfig(level=logging.INFO)


def configure_telegram():
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TELEGRAM_TOKEN:
        logger.error('environment variable `TELEGRAM_TOKEN` must be set')
        raise NotImplementedError

    return telegram.Bot(TELEGRAM_TOKEN)


def handler(event, context):
    bot = configure_telegram()
    logger.info('event: {}'.format(event))

    if event.get('httpMethod') == 'POST' and event.get('body'):
        logger.info('message received')

        update = telegram.Update.de_json(json.loads(event.get('body')), bot)

        plain_handler(bot, update, logger)

        return OK_RESPONSE

    return ERROR_RESPONSE


def set_webhook(url):
    logger.info('url: {}'.format(url))

    bot = configure_telegram()
    webhook = bot.set_webhook(url)

    if webhook:
        return OK_RESPONSE

    return ERROR_RESPONSE
