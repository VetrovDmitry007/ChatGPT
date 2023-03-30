import sqlite3
import os
from pprint import pprint
from typing import List, Tuple, Dict
from datetime import datetime


class SQLite:

    def __init__(self, rebuild=False):
        if rebuild:
            if os.path.exists('chatQR.db'):
                os.remove('chatQR.db')
            self.conn = sqlite3.connect('chatQR.db')
            self._createTab()
        else:
            if not os.path.exists('chatQR.db'):
                self.conn = sqlite3.connect('chatQR.db')
                self._createTab()
            else:
                self.conn = sqlite3.connect('chatQR.db')

    def _createTab(self):
        # Таблица основных запросов
        print('_createTab: quest_pr')
        c = self.conn.cursor()
        c.execute('''CREATE TABLE quest_pr(id INTEGER PRIMARY KEY AUTOINCREMENT, question text, 
        embed text)''')
        self.conn.commit()
        # Таблица вариаций основных запросов
        print('_createTab: quest_sc')
        c.execute('''CREATE TABLE quest_sc(id INTEGER PRIMARY KEY AUTOINCREMENT, quest_pr_id INTEGER, question text, 
        embed text, FOREIGN KEY (quest_pr_id) REFERENCES quest_pr (id))''')
        self.conn.commit()
        # Таблица ответов на основные запросы
        print('_createTab: answer_pr')
        c.execute('''CREATE TABLE answer_pr(id INTEGER PRIMARY KEY AUTOINCREMENT, quest_pr_id INTEGER, 
                answer text, FOREIGN KEY (quest_pr_id) REFERENCES quest_pr (id))''')
        self.conn.commit()

    def addRec(self, tab, **dc_val):
        """ Добавляет запись в таблицу Db
        :param tab: Имя таблицы
        :param dc_val: Словарь {столбец: значение}
        :return: boool
        """
        c = self.conn.cursor()
        ls_col = list(dc_val.keys())
        if len(ls_col)>1:
            col = ', '.join(ls_col)
        else:
            col = ls_col[0]

        ls_val = [s.replace('"','') for s in dc_val.values()]
        ls_val = list(map(lambda s: '"' + s + '"', ls_val))  # добавляем кавычки
        val = ', '.join(ls_val)
        # if len(ls_val) > 1:
        #     ls_val = list(map(lambda s: '"' + s + '"', ls_val))  # добавляем кавычки
        #     val = ', '.join(ls_val)
        # else:
        #     val = ls_val[0]

        sql = f"INSERT INTO {tab}({col}) VALUES ({val})"
        c.execute(sql)
        self.conn.commit()
        return True

    def simpleReq(self, sql: str) -> List:
        """ Выполняет произвольный запрос
        :return: Список записей
        """
        c = self.conn.cursor()
        c.execute(sql)
        self.conn.commit()
        return c.fetchall()


if __name__ == '__main__':
    sql = SQLite()
    # dc = {'question': 'Где находится организация ~Рога и Копыта~ '}
    # sql.simpleReq('delete from quest_pr')
    # sql.addRec('quest_pr', **dc)

    # ls = sql.simpleReq('select  * from quest_pr')
    # ls = sql.simpleReq('select  * from quest_sc')
    ls = sql.simpleReq('select  * from answer_pr')

    # fild = 'Какие услуги предоставляет Фирма Рога и копыта?'
    # ls =sql.simpleReq(f'select id from quest_pr where question = "{fild}"')[0][0]
    # pprint(ls)

    # dc = {'answer': 'Фирма Рога и Копыта оказывает услуги по организации пеших эротических туров.', 'quest_pr_id': '15'}
    # sql.addRec('answer_pr', **dc)

    # ls = sql.simpleReq('select  * from answer_pr')
    pprint(ls)
