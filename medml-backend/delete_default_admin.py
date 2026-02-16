import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.models import db, User

def delete_default_admin():
    app = create_app('development')
    with app.app_context():
        admin = User.query.filter_by(email='admin@healthcare.com').first()
        if admin:
            db.session.delete(admin)
            db.session.commit()
            print("SUCCESS: Default admin user deleted.")
        else:
            print("INFO: Default admin user not found.")

if __name__ == '__main__':
    delete_default_admin()
