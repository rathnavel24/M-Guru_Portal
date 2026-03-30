from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

conn  = os.getenv("DB_CONNECTION")


if conn and "pgbouncer=" in conn.lower():
    conn = conn.split("?")[0]
engine  = create_engine(conn,pool_pre_ping=True)

sessionLocal = sessionmaker(autocommit=False,
    autoflush=False,bind = engine)



