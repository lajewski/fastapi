import psycopg2
from psycopg2.extras import RealDictCursor
from .config import settings
import time
#sqlalchemy specific imports
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker


def database_connection():
    while True:
        try:
            conn = psycopg2.connect(host=settings.database_hostname, database=settings.database_name,port=settings.database_port,user=settings.database_username, password=settings.database_password, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            print("Database connection was successful!")
            return conn
            break
        except Exception as error:
            print("Connecting to database failed")
            print("Error: ", error)
            time.sleep(2)   




# SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'


# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
