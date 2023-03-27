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
        print('_createTab: qu_an')
        c = self.conn.cursor()
        c.execute('''CREATE TABLE qu_an(id INTEGER PRIMARY KEY AUTOINCREMENT, date_cr text, question text, 
        answer_1 text, answer_2 text, answer_3 text, pad_question text)''')
        self.conn.commit()

    def addRec(self, tab, **dc_val):
        """ Добавляет запись в таблицу Db
        :param tab: Имя таблицы
        :param dc_val: Словарь {столбец: значение}
        :return: boool
        """
        c = self.conn.cursor()
        dc_val.update({'date_cr': datetime.now().strftime("%Y-%m-%d_%H-%M-%S")})
        col = ', '.join(dc_val.keys())
        col_val = list(map(lambda s: '"' + s + '"', dc_val.values()))  # добавляем кавычки
        col_val = ', '.join(col_val)
        c.execute(f"INSERT INTO {tab}({col}) VALUES ({col_val})")
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
    dc = {'question': 'Где находится организация "Рога и Копыта" '}
    # sql.simpleReq('delete from qu_an')
    # sql.addRec('qu_an', **dc)
    ls = sql.simpleReq('select  * from qu_an')
    pprint(ls)
