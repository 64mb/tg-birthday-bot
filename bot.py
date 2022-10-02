import traceback

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from api import quiz


def plain_handler(bot, update, logger):
    try:
        text = update.message.text
        chat_id = update.message.chat_id

        bot.send_chat_action(
            chat_id=chat_id, action=telegram.ChatAction.TYPING)

        if text == '/start':
            quiz.begin_start(chat_id)
            message, video = quiz.next_step(chat_id, True)

            bot.send_message(
                chat_id=chat_id,
                text=message
            )

            if video:
                bot.send_video(chat_id=chat_id, video=video,
                               supports_streaming=True)
            return

        check = quiz.check_answer(chat_id,  text)
        if check:
            quiz.answer_success(chat_id)
        else:
            quiz.answer_error(chat_id)

        message, video = quiz.next_step(chat_id, check)

        if video:
            bot.send_video(chat_id=chat_id, video=video,
                           supports_streaming=True)

        bot.send_message(
            chat_id=chat_id,
            text=message
        )

    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

    return
