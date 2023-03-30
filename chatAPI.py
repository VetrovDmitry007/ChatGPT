"""
Подготовка вопросов и ответов по описанию деятельности фирмы
"""
from pprint import pprint

import openai
import re

import torch
from sentence_transformers import SentenceTransformer, util
from typing import List, Tuple, Dict
from SQLite import SQLite
import setup

model_eval = SentenceTransformer('distiluse-base-multilingual-cased-v1')


class GPT:

    def __init__(self, discr_ltd: str):
        openai.api_key = setup.api_key
        self.pre_fix = "В тебя заложена следующая информация."
        self.discr_ltd = discr_ltd
        self.post_fix = "Ты услужливый, творческий, умный и очень дружелюбный ИИ-помощник данной фирмы."
        self.cn_question = setup.cn_question
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
        ls = [re.sub(r'\A\d+[.)]{1}', '', s) for s in ls]
        ls = [s.strip() for s in ls]
        return ls

    def get_quest_sc(self, quest) -> List[str]:
        """ Возвращает список синонимов возможных вопросов

        :return:
        """
        new_descr = f'{self.discr_ltd} {self.post_fix} Составь 20 вариантов вопроса "{quest}"'
        res = self.get_response(new_descr)
        ls = res.split('\n')
        # Удаление нумерации
        ls = [re.sub(r'\A\d+[.)]{1}', '', s) for s in ls]
        ls = [s.strip() for s in ls]
        return ls

    def ins_quest(self, ls_quest: List[str]):
        """ Добавляет возможные вопросы в базу

        :param ls_quest: список возможных вопросов
        :return:
        """
        for question in ls_quest:
            # question = question.replace('"', "'")
            dc = {'question': question}
            self.sql.addRec('quest_pr', **dc)

    def get_quest_id(self, fild:str):
        """ Получение id вопроса

        :param fild:
        :return:
        """
        # fild = fild.replace('"', "'")
        id = self.sql.simpleReq(f'select id from quest_pr where question = "{fild}"')[0][0]
        return str(id)

    def ins_answer(self, question, ls_answer: List[str]):
        """ Добавляет возможные ответы в базу

        :param ls_quest: список возможных ответов
        :return:
        """
        id = self.get_quest_id(question)
        for answer in ls_answer:
            dc = {'answer': answer, 'quest_pr_id':id}
            self.sql.addRec('answer_pr', **dc)

    def ins_quest_sc(self, question, ls_quest_sc: List[str]):
        """ Добавляет возможные ответы в базу

        :param ls_quest: список возможных ответов
        :return:
        """
        id = self.get_quest_id(question)
        for quest in ls_quest_sc:
            dc = {'question': quest, 'quest_pr_id':id}
            self.sql.addRec('quest_sc', **dc)

    def get_answ(self, quest) -> List[str]:
        """ Возвращает список возможных ответов

        :param quest:
        :return:
        """
        prm = f'{self.pre_fix} {self.discr_ltd} Как по разному могла бы ты ответить на вопрос. "{quest}"' \
              f' Предоставь не менее 3-х развёрнутых вариантов ответа. В каждом ответе одно предложение.'
        res = self.get_response(prm)
        ls = res.split('\n')
        # Удаление нумерации
        ls = [re.sub(r'\A\d+[.)]{1}','',s) for s in ls]
        ls = [s.strip() for s in ls]
        return ls

    def init_db(self):
        """ Начальное заполнение базы

        :return:
        """
        self.sql.simpleReq('delete from quest_sc')
        self.sql.simpleReq('delete from answer_pr')
        self.sql.simpleReq('delete from quest_pr')
        print('Начальное заполнение базы.')
        print('1. Генерация возможных вопросов.')
        ls_quest = self.get_quest()
        print(f'Создано {len(ls_quest)} вопросов.')
        self.ins_quest(ls_quest)
        print('Вопросы занесены в базу.')
        print('2. Генерация возможных ответов.')
        for cn, quest in enumerate(ls_quest, start=1):
            print(f'2.{cn}. Генерация ответов на вопрос: {quest}')
            ls_answ = self.get_answ(quest)
            self.ins_answer(quest, ls_answ)
        print('Ответы занесены в базу.')
        print('3. Генерация вариаций основных вопросов.')
        for cn, quest in enumerate(ls_quest, start=1):
            print(f'3.{cn}. Генерация синонимов вопроса: {quest}')
            ls_quest_sc = self.get_quest_sc(quest)
            self.ins_quest_sc(quest, ls_quest_sc)
        print('Синонимы вопросов занесены в базу.')

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
    """ Нахождение ближайшего схожего вопроса

    """
    # query = 'Кто ваш директор'
    query = 'Как вас найти'
    # query = 'Как до вас доехать'
    query_embedding = model_eval.encode(query, device='cpu')
    st ="""
        Как зовут вашего директора?
        Где находится ваша фирма?
        Можете сказать, где расположена ваша компания?
        Где находится офис вашей компании?
        Где я могу найти вашу фирму?
        В каком районе находится ваша компания?
        Как мне добраться до вашей фирмы?
        Какой адрес вашей компании?
        Где я могу найти вашу фирму на карте?
        Где расположен ваш бизнес-центр?
        Как я могу найти ваш офис?
        Где находится ваше представительство?
        Как мне найти вашу компанию?
        Где расположена ваша головная офис?
        Какой индекс у вашего офиса?
        В каком здании находится ваш офис?
        Как мне добраться до вашего офиса на общественном транспорте?
        Где находится ваша основная база?
        Как я могу найти вашу фирму в Интернете?
        Где находится ваш центральный офис?
        Где находится ваш филиал в этом городе?
        """
    ls = st.split('\n')
    passage_embedding = model_eval.encode(ls, device='cpu')

    tensor = util.dot_score(query_embedding, passage_embedding)
    print("Сходство:", tensor)
    print("Вопрос:", query)
    print(f"Схожий вопрос: {ls[torch.argmax(tensor)].strip()}, номер: {torch.argmax(tensor)}")
    print(f'mean + std/2: {tensor.mean() + tensor.std() / 2}')
    print(f'std: {tensor.std()}')
    print(f'mean : {tensor.mean()}')
    print(f'tensor > 0,5: { tensor[tensor > 0.5]  }')


def test_bert_2():
    """ Косинусная близость между вопросом
    и средне-арифметическим эмбединга списка аналогичных вопросов
    """
    # query_embedding = model_eval.encode('Как вас найти', device='cpu')
    # query_embedding = model_eval.encode('До которого часа вы работаете', device='cpu')
    # query_embedding = model_eval.encode('Кто ваш директор', device='cpu')
    query_embedding = model_eval.encode('Как до вас доехать', device='cpu')
    st ="""
        Где находится ваша фирма?
        Можете сказать, где расположена ваша компания?
        Где находится офис вашей компании?
        Где я могу найти вашу фирму?
        В каком районе находится ваша компания?
        Как мне добраться до вашей фирмы?
        Какой адрес вашей компании?
        Где я могу найти вашу фирму на карте?
        Где расположен ваш бизнес-центр?
        Как я могу найти ваш офис?
        Где находится ваше представительство?
        Как мне найти вашу компанию?
        Где расположена ваша головная офис?
        Какой индекс у вашего офиса?
        В каком здании находится ваш офис?
        Как мне добраться до вашего офиса на общественном транспорте?
        Где находится ваша основная база?
        Как я могу найти вашу фирму в Интернете?
        Где находится ваш центральный офис?
        Где находится ваш филиал в этом городе?
        """
    ls = st.split('\n')
    ls_query = [s.strip() for s in ls if len(s)>1]
    print(ls_query)

    passage_embedding = model_eval.encode(ls_query, device='cpu')
    mean_embedding = passage_embedding.mean(axis=0)

    print("Сходство:", util.dot_score(query_embedding, mean_embedding))


if __name__ == '__main__':
    discr_ltd = """
      Фирма Рога и копыта находится в городе Орёл на улице Октябрьская д.10. Директора зовут
      Иванов Сергей Николаевич. Часы работы с 8.00 до 17.00. Обеденный перерыв
      с 13.00 до 14.00. Фирма оказывает услуги по организации пеших эротических туров.
      Телефон приёмной: 8(910)455-99-77.
      """
    gpt = GPT(discr_ltd)
    gpt.init_db()
    # ls = gpt.get_quest()
    # pprint(ls)
    # ls = gpt.get_quest_sc(ls[0])
    # ls = gpt.get_quest_sc("Какие услуги оказывает Фирма Рога и копыта?")
    # ls = gpt.sql.simpleReq('select question from qu_an')
    # pprint(ls)

    # test_bert()
    # test_bert_2()
