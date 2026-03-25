from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

conn  = os.getenv("DB_CONNECTION")
engine  = create_engine(conn)

sessionLocal = sessionmaker(bind = engine)