from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import setting

db_username = setting.database_username
db_passwd = setting.database_password
db_hostname = setting.database_hostname
db_port = setting.database_port
db_name = setting.database_name
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_username}:{db_passwd}@{db_hostname}:{db_port}/{db_name}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()