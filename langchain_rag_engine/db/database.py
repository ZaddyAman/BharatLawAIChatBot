from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
# Get absolute path to ensure we're using the correct database
# Use the main database in the project root instead of langchain_rag_engine specific db
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_PATH = os.path.join(PROJECT_ROOT, "sql_app.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

print(f"[DATABASE] Using database at: {DATABASE_PATH}")
print(f"[DATABASE] File exists: {os.path.exists(DATABASE_PATH)}")
print(f"[DATABASE] Current working directory: {os.getcwd()}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    import langchain_rag_engine.db.models as models
    Base.metadata.create_all(bind=engine)
