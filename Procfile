web: python -c "from app import app; from utils.database import db; app.app_context().push(); db.create_all(); print('Database initialized')" && gunicorn --bind 0.0.0.0:$PORT app:app
