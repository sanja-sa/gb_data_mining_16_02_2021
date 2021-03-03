import queue as qu
from abc import abstractmethod
import time
from urllib.parse import urljoin
from datetime import datetime
from bs4 import BeautifulSoup as soup
import json


class TaskBase:
    """
    Класс базовый для всех классов задач
    """
    def __init__(self, queue):
        self.queue = queue


class TaskMain(TaskBase):
    """
    Класс задачи получения информации по навигации постов
    и генерации задач для обхода постов
    и генерации задач для обхода по пагинации
    """
    def __init__(self, url:str, source_stream, queue):
        super().__init__(queue)
        self.url = url
        self.source_stream = source_stream

    def __call__(self):
        print("Parse page: " + self.url)
        raw_content = self.source_stream(self.url)
        if raw_content is None: return
        structured_content = soup(raw_content, "lxml")

        # Posts
        posts_blocks = structured_content.find_all("div", {"class": "post-item event"})
        for post in posts_blocks:
            self.queue.add_post_task(post.a['href'])

        # Pagination
        next_page_block = structured_content.find_all("li", {"class": "page"})
        if next_page_block is None or len(next_page_block) == 1: return
        self.queue.add_main_task(next_page_block[len(next_page_block)-1].a['href']) 


class TaskPost(TaskBase):
    """
    Класс задачи получения информации по постам и дальнейшей обработки этих задач
    """
    def __init__(self, url:str, callback, source_stream, queue):
        super().__init__(queue)
        self.callback = callback
        self.url = url
        self.source_stream = source_stream

    def _parse(self, content):
        block_content = json.loads(content.find("div", {"class": "page-content"}, recursive=True).script.string)
        block_tags = json.loads(content.find("div", {"class": "gb-topics m-b-md"}, recursive=True).script.string)
        return {
                "post_data":{
                    "url" : block_content["url"],
                    "img_url" : block_content["image"]["url"],
                    "title" : block_content["headline"],
                    "published_dt" : datetime.fromisoformat(block_content["datePublished"]),
                    "id" : int(block_content["image"]["url"].split('/')[4])
                },
                "author_data":{
                    "name" : block_content["author"]["name"],
                    "url" : block_content["author"]["url"],
                },
                "tags_data":[{'name':tag} for tag in block_tags["tags"]]
        }

    def __call__(self):
        print("Parse post: " + self.url)
        raw_content = self.source_stream(self.url)
        if raw_content is None: return
        structured_content = soup(raw_content, "lxml")
        post = {}
        try:
            post = self._parse(structured_content)
        except:
            # TODO: Ошибка
            return
        self.callback(post)
        self.queue.add_comments_task("/api/v2/comments?commentable_type=Post&commentable_id="+str(post["post_data"]["id"])+"&order=desc", post["post_data"]["id"])


class TaskComments(TaskBase):
    """
    Класс задачи получения информации по комментариям
    """
    def __init__(self, url:str, post_id:int, callback, source_stream, queue):
        super().__init__(queue)
        self.callback = callback
        self.url = url
        self.post_id = post_id
        self.source_stream = source_stream

    def _parse_comment(self, comment):
        data = comment['comment']
        itm = { 
                "post_data":{
                    "id":self.post_id,
                },
                "comment_data":{
                    "id":data['id'],
                    "parent_id":data['parent_id'],
                    "comment":data['body'],
                    "author_name" : data["user"]["full_name"],
                    "author_url" : data["user"]["url"]
                }
        }
        self.callback(itm)
        for comment in data['children']:
            self._parse_comment(comment)

    def __call__(self):
        print("Parse comments: " + self.url)
        raw_content = self.source_stream(self.url)
        if raw_content is None: return
        structured_content = json.loads(raw_content)
        for comment in structured_content:
            self._parse_comment(comment)

class TaskQueue:
    """
    Класс очереди для обхода задач
    """
    def __init__(self, callback_post, callback_comments, source_stream):
        self.tasks_queue = qu.Queue()
        self.callback_post = callback_post
        self.callback_comments = callback_comments
        self.source_stream = source_stream

    def __call__(self, start_url:str):
        self.add_main_task(start_url)        
        while not self.tasks_queue.empty():
            self.tasks_queue.get()()
            time.sleep(1)

    # TODO: Сделать фабрику
    def add_main_task(self, url:str):
        return self.tasks_queue.put(TaskMain(url, self.source_stream, self))

    def add_post_task(self, url:str) -> TaskPost:
        return self.tasks_queue.put(TaskPost(url, self.callback_post, self.source_stream, self))

    def add_comments_task(self, url:str, post_id:int) -> TaskComments:
        return self.tasks_queue.put(TaskComments(url, post_id, self.callback_comments, self.source_stream, self))
