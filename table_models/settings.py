from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from table_models.users import Words, Translations, UserTranslations, Users, UserWords

from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


def init_db():
    from table_models.users import Base  #
    Base.metadata.create_all(bind=engine)
