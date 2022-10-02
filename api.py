
import datetime
import json
from difflib import SequenceMatcher

from db import db


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class quiz:
    @staticmethod
    def get_default_data():
        questions = json.loads(open('questions.json').read())
        return questions

    @staticmethod
    def begin_start(user_id):
        quiz.save_user(user_id, quiz.get_default_data())
        return

    @staticmethod
    def get_user(user_id):
        user = db.get_user(user_id)

        if user is None:
            user = quiz.save_user(user_id, quiz.get_default_data())

        user['questions'] = json.loads(user['questions'])

        return user

    @staticmethod
    def save_user(user_id, data):
        d = data
        d['questions'] = json.dumps(data['questions'], ensure_ascii=False)

        user = db.save_user(user_id, data)

        return user

    @staticmethod
    def answer_success(user_id):
        user = quiz.get_user(user_id)

        if user['step'] in user['questions']:
            user['step'] = str(int(user['step'])+1)
        user['errors'] = '0'

        quiz.save_user(user_id, user)

        return

    @staticmethod
    def answer_error(user_id):
        user = quiz.get_user(user_id)

        user['errors'] = int(user['errors'])+1

        helps = user['questions'][user['step']]['help']
        if user['errors'] >= len(helps):
            user['errors'] = len(helps)

        user['errors'] = str(user['errors'])

        quiz.save_user(user_id, user)

        return

    @staticmethod
    def next_step(user_id, success=False):
        user = quiz.get_user(user_id)

        next_text = ''
        video = None

        if success:
            if user['step'] in user['questions']:
                next_step = next_text = user['questions'][user['step']]
                next_text = next_step['question']
                if 'video' in next_step:
                    video = next_step['video']
            else:
                next_text = user['final']
        else:
            helps = user['questions'][user['step']]['help']
            for i in range(0, int(user['errors'])):
                next_text += helps[i]+'\n'

        return next_text, video

    @staticmethod
    def check_answer(user_id, answer):
        user = quiz.get_user(user_id)

        answer = answer.lower()

        is_good = False

        if user['step'] in user['questions']:
            good_answer = user['questions'][user['step']]['answer']
            good_answer = good_answer.lower()
            if similar(answer, good_answer) > 0.65:
                is_good = True
        else:
            is_good = True

        return is_good
