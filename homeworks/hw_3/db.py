from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


class Database:
    def __init__(self, endpoint:str):
        engine = create_engine(endpoint)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def _get(self, session, model, u_field, u_value, **data):
        return session.query(model).filter(u_field==data[u_value]).first()        

    def _get_or_create(self, session, model, u_field, u_value, **data):
        db_data = session.query(model).filter(u_field==data[u_value]).first()
        if not db_data:
            db_data = model(**data)
        return db_data

    def create_post(self, data):
        session = self.maker()

        author = self._get_or_create(
            session, 
            models.Author,
            models.Author.url,
            "url",
            **data["author_data"]
            )

        post = self._get_or_create(
            session, 
            models.Post,
            models.Post.url,
            "url",
            **data["post_data"],
            author=author
            )
            
        post.tags.extend(map(lambda tag_data: self._get_or_create(
            session,
            models.Tag,
            models.Tag.name,
            "name",
            **tag_data
        ), data["tags_data"]))

        session.add(post)

        try:
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()
  
    def create_comment(self, data):
        session = self.maker()

        post = self._get(
            session, 
            models.Post,
            models.Post.id,
            "id",
            **data["post_data"],
            )

        comment = self._get_or_create(
            session, 
            models.Comment,
            models.Comment.id,
            "id",
            **data["comment_data"],
            post=post,
            )

        session.add(comment)

        try:
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()