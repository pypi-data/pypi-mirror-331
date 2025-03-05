from sqlmodel import Session, SQLModel, create_engine

DEFAULT_CONFIG = {
    "sqlite_url": "sqlite:///database.db"
}

engine = create_engine(DEFAULT_CONFIG["sqlite_url"])

def connect_db():
    engine = create_engine(DEFAULT_CONFIG["sqlite_url"])

def create_db_and_tables():
    # SQLModel.metadata.create_all() has checkfirst=True by default
    # so tables will only be created if they don't exist
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session