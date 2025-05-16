from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./main.db"

engine = create_engine(url=DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)



