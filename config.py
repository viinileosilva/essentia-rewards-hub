import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'essentia-2024-seguro')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _db_url = os.environ.get('DATABASE_URL', '')

    if _db_url:
        # Render fornece DATABASE_URL com prefixo antigo "postgres://"
        SQLALCHEMY_DATABASE_URI = _db_url.replace('postgres://', 'postgresql://', 1)
    else:
        # Localmente usa SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'essentia.db')

    USE_TURSO = False
