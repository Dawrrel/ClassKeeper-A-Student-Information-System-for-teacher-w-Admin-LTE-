# create_admin.py

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Replace these values with your admin credentials
    admin_username = 'admin'
    admin_email = 'admin@example.com'
    admin_password = generate_password_hash('admin_password')

    # Check if admin already exists
    admin = User.query.filter_by(email=admin_email).first()
    if admin is None:
        # Create a new admin user
        new_admin = User(username=admin_username, email=admin_email, password=admin_password, is_admin=True)
        db.session.add(new_admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")
