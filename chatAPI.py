"""
Подготовка вопросов и ответов по описанию деятельности фирмы
"""
import openai
import re
from sentence_transformers import SentenceTransformer, util
from typing import List, Tuple, Dict
from SQLite import SQLite

model_eval = SentenceTransformer('distiluse-base-multilingual-cased-v1')


class GPT:

    def __init__(self, discr_ltd: str):
        openai.api_key = "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"
        self.pre_fix = "В тебя заложена следующая информация."
        self.discr_ltd = discr_ltd
        self.post_fix = "Ты услужливый, творческий, умный и очень дружелюбный ИИ-помощник данной фирмы."
        self.cn_question = 20
        self.sql = SQLite()

    def get_quest(self) -> List[str]:
        """ Возвращает список возможных вопросов

        :return:
        """
        new_descr = f'{self.pre_fix} {self.discr_ltd} {self.post_fix} Составь список из {self.cn_question} вопросов,\
            которые задал бы тебе пользователь.'
        res = self.get_response(new_descr)
        ls = res.split('\n')
        # Удаление нумерации
        ls_quest = list(map(lambda x: re.split(r'\d+[.]{1}', x)[1].strip(), ls))
        return ls_quest

    def ins_quest(self, ls_quest: List[str]):
        """ Добавляет возможные вопросы в базу

        :param ls_quest: список возможных вопросов
        :return:
        """
        for question in ls_quest:
            question = question.replace('"', "'")
            dc = {'question': question}
            self.sql.addRec('qu_an', **dc)

    def get_answ(self, quest) -> List[str]:
        """ Возвращает список возможных ответов

        :param quest:
        :return:
        """
        prm = f'{self.pre_fix} {self.discr_ltd} Как по разному могла бы ты ответить на вопрос. "{quest}"' \
              f' Предоставь не менее 3-х вариантов ответа. В каждом ответе одно предложение.'
        res = self.get_response(prm)
        ls = res.split('\n')
        # Удаление нумерации
        ls_answer = list(map(lambda x: re.split(r'\d+[.]{1}', x)[1].strip(), ls))
        return ls_answer

    def init_db(self):
        """ Начальное заполнение базы

        :return:
        """
        print('Начальное заполнение базы.')
        print('1. Генерация возможных вопросов.')
        ls_quest = self.get_quest()
        print(f'Создано {len(ls_quest)} вопросов.')
        self.ins_quest(ls_quest)
        print('Вопросы занесены в базу.')
        print('2. Генерация возможных ответов.')

    def get_response(self, msg):
        """ Формирование запроса в ChatGPT

        :param msg: Вопрос
        :return: Ответ
        """
        response = openai.Completion.create(
            model="text-davinci-003",
            # model="text-davinci-002",
            prompt=msg,
            temperature=0.7,
            max_tokens=1024,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=1,
        )
        message = response.choices[0].text.strip()
        return message


def test_bert():
    # discr_ltd = """
    #   Фирма "Рога и копыта" находится в городе Орёл на улице Октябрьская д.10. Директора зовут
    #   Иванов Сергей Николаевич. Часы работы с 8.00 до 17.00. Обеденный перерыв
    #   с 13.00 до 14.00. Фирма оказывает услуги по организации пеших эротических туров.
    #   Телефон приёмной: 8(910)455-99-77.
    #   """
    # discr_ltd = "До которого часа вы работаете"
    discr_ltd = "Как вас найти"
    query_embedding = model_eval.encode(discr_ltd, device='cpu')
    passage_embedding = model_eval.encode(["Где находится фирма 'Рога и Копыта'",
                                           'Каково имя директора фирмы?',
                                           'Какие услуги предоставляет фирма?',
                                           'Какие часы работы?',
                                           'Есть ли обеденный перерыв?'], device='cpu')

    print("Сходство:", util.dot_score(query_embedding, passage_embedding))


if __name__ == '__main__':
    discr_ltd = """
      Фирма "Рога и копыта" находится в городе Орёл на улице Октябрьская д.10. Директора зовут 
      Иванов Сергей Николаевич. Часы работы с 8.00 до 17.00. Обеденный перерыв 
      с 13.00 до 14.00. Фирма оказывает услуги по организации пеших эротических туров. 
      Телефон приёмной: 8(910)455-99-77.   
      """
    # gpt = GPT(discr_ltd)
    # gpt.init_db()
    # ls = gpt.get_quest()
    # print(ls[10])
    # ls = gpt.get_answ('Предлагаются ли групповые туры?')
    # ls = gpt.sql.simpleReq('select  question from qu_an')
    # print(ls)
    test_bert()
