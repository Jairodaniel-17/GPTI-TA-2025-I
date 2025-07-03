import os


class Config:
    # Configuración básica
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-key-very-secret"

    # Configuración de SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///pmbok.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de carga de archivos
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "static/uploads"
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
