import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'essentia-rewards-secret-2024')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL', '')
    TURSO_AUTH_TOKEN   = os.environ.get('TURSO_AUTH_TOKEN', '')
    USE_TURSO = bool(TURSO_DATABASE_URL and TURSO_AUTH_TOKEN)

    # Quando Turso estiver configurado usamos 'sqlite://' como placeholder de dialeto;
    # o engine real é criado via `creator` em app/__init__.py
    SQLALCHEMY_DATABASE_URI = (
        'sqlite://'
        if USE_TURSO
        else 'sqlite:///' + os.path.join(BASE_DIR, 'essentia.db')
    )
