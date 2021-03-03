'''
Источник https://geekbrains.ru/posts/
Необходимо обойти все записи в блоге и извлеч из них информацию следующих полей:

url страницы материала
Заголовок материала
Первое изображение материала (Ссылка)
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
комментарии в виде (автор комментария и текст комментария)
список тегов

реализовать SQL структуру хранения данных c следующими таблицами
Post
Comment
Writer
Tag
Организовать реляционные связи между таблицами

При сборе данных учесть, что полученый из данных автор уже может быть в БД и значит необходимо это заблаговременно проверить.
Не забываем закрывать сессию по завершению работы с ней
'''

import requests
import time
import re
from urllib.parse import urljoin
from datetime import datetime
import path
import db
from gb_tasks import TaskQueue


class CallBackPosts:
    def __init__(self, db):
        self.db = db

    def __call__(self, post:dict):
        self.db.create_post(post)


class CallBackComment:
    def __init__(self, db):
        self.db = db

    def __call__(self, comment:dict):
        self.db.create_comment(comment)
        

class SourceStream:
    def __init__(self, root_url:str):
        self.root_url = root_url

    def __call__(self, url:str, params=None):
        url = urljoin(self.root_url, url),
        while True:
            response = requests.get(url[0])
            if (response.status_code//10) == 20:
                return response.content
            time.sleep(1.2)

if __name__ == '__main__':
    db = db.Database("sqlite:///gb_blog.db")
    task_queue = TaskQueue(CallBackPosts(db), CallBackComment(db), SourceStream("https://geekbrains.ru/"))
    task_queue("/posts?page=1")
