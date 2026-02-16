
import os
import sys
from flask import Flask

# Add the current directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import User

def create_admin():
    app = create_app('development')
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.objects(email='admin@healthcare.com').first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.email}")
            # Reset password just in case
            existing_admin.set_password('Admin123!')
            existing_admin.save()
            print("Password reset to: Admin123!")
            return
        
        # Create new admin
        admin = User(
            name='System Administrator',
            email='admin@healthcare.com',
            username='admin',
            designation='System Administrator',
            contact_number='+91-9876543210',
            facility_name='Healthcare Management System',
            role='admin'
        )
        admin.set_password('Admin123!')
        
        try:
            admin.save()
            print("SUCCESS: Admin user created successfully!")
            print("Email:    admin@healthcare.com")
            print("Username: admin")
            print("Password: Admin123!")
        except Exception as e:
            print(f"ERROR: Error creating admin user: {e}")

if __name__ == '__main__':
    create_admin()
