from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

Base = declarative_base()


class Words(Base):
    __tablename__ = 'words'
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(unique=True)
    translations = relationship('Translations', back_populates='words')
    users = relationship('UserWords', back_populates='word')


class Translations(Base):
    __tablename__ = 'translations'
    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey('words.id'), unique=True)
    translation: Mapped[str] = mapped_column(unique=True)
    words = relationship('Words', back_populates='translations')


class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    translations = relationship('UserTranslations', back_populates='user')
    words = relationship('UserWords', back_populates='user')


class UserTranslations(Base):
    __tablename__ = 'user_translation'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    translation_id: Mapped[int] = mapped_column(ForeignKey('translations.id'))
    is_correct: Mapped[bool] = mapped_column()
    user = relationship('Users', back_populates='translations')


class UserWords(Base):
    __tablename__ = 'user_words'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey('words.id'), primary_key=True)
    user = relationship('Users', back_populates='words')
    word = relationship('Words', back_populates='users')
