from sqlmodel import SQLModel, create_engine, Session

# SQLite file
DATABASE_URL = "sqlite:///./notes.db"

connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
