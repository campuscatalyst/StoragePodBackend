from sqlmodel import SQLModel, create_engine, Session
from app.logger import logger
from contextlib import contextmanager

DATABASE_URL = "sqlite:////app/db/data/main.db"

engine = create_engine(url=DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    logger.info(f"Creating the db at - {DATABASE_URL}")
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()





