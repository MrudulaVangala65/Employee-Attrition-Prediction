from flask_sqlalchemy import SQLAlchemy
from app import app, db, User  # replace with your actual app file name

with app.app_context():
    user = User.query.filter(User.username.ilike("admin")).first()
    if user:
        user.password = "Lalitha"
        db.session.commit()
        print("✅ Admin credentials updated.")
    else:
        print("⚠️ Admin user not found.")
