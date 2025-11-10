"""Drop all tables and recreate database."""
from app import create_app, db

app = create_app('development')
with app.app_context():
    db.drop_all()
    db.create_all()