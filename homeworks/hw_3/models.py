from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table


Base = declarative_base()


tag_post = Table(
    "tag_post", 
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")), 
    Column("tag_id", Integer, ForeignKey("tag.id"))
    )


class IdMixin:
    id = Column(Integer, primary_key=True)


class UrlMixin:
    url = Column(String, nullable=False, unique=True)


class NameMixin:
    name = Column(String, nullable=False)


class Post(Base, IdMixin, UrlMixin):
    __tablename__ = "post"
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    img_url = Column(String, nullable=False)
    published_dt = Column(DateTime)
    author_id = Column(Integer, ForeignKey("author.id"))
    author = relationship("Author")
    tags = relationship("Tag", secondary=tag_post)


class Author(Base, UrlMixin, NameMixin):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, autoincrement=True)
    posts = relationship("Post")


class Tag(Base, NameMixin):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tags = relationship("Post", secondary=tag_post)


class Comment(Base, IdMixin):
    __tablename__ = "comment"

    comment = Column(String, nullable=False)
    author_name = Column(String, nullable=False)
    author_url = Column(String, nullable=False)
    parent_id = Column(Integer)
    
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post")
