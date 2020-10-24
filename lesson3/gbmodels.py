from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    Date,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

tag_post_table = Table(
    'tag_post_table',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

comments_table = Table(
    'comments_table',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('comment_id', Integer, ForeignKey('comment.id'))
)


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, unique=False, nullable=False)
    description = Column(String, unique=False, nullable=True)
    title_img = Column(String, unique=False, nullable=True)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship('Writer', back_populates='posts')
    tag = relationship('Tag', secondary=tag_post_table)
    comment = relationship('Comment', secondary=comments_table)
    published_at = Column(Date, unique=False, nullable=False)


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False, default='GeekBrains')
    url = Column(String, unique=True, nullable=False)
    posts = relationship('Post')
    comments = relationship('Comment')


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship('Post', secondary=tag_post_table)


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, autoincrement=True, primary_key=True)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship('Writer', back_populates='comments')
    posts = relationship('Post', secondary=comments_table)


if __name__ == '__main__':
    print(1)
