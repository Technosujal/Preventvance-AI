#!/usr/bin/env python3
"""
Script to create an initial admin user for the Healthcare Management System.
Run this script to set up the first admin account.
"""

import os
import sys
from flask import Flask
from flask_bcrypt import Bcrypt

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.models import db, User
from app.config import config

def create_admin():
    """Create the initial admin user."""
    app = create_app('development')
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(email='admin@healthcare.com').first()
        if existing_admin:
            print("Admin user already exists!")
            print(f"Email: {existing_admin.email}")
            print(f"Username: {existing_admin.username}")
            print("You can use these credentials to log in.")
            return
        
        # Create new admin
        bcrypt = Bcrypt()
        password_hash = bcrypt.generate_password_hash('Admin123!').decode('utf-8')
        
        admin = User(
            name='System Administrator',
            email='admin@healthcare.com',
            username='admin',
            password_hash=password_hash,
            designation='System Administrator',
            contact_number='+91-9876543210',
            facility_name='Healthcare Management System',
            role='admin'
        )
        
        try:
            db.session.add(admin)
            db.session.commit()
            
            print("SUCCESS: Admin user created successfully!")
            print("\nLogin Credentials:")
            print("=" * 40)
            print(f"Email:    admin@healthcare.com")
            print(f"Username: admin")
            print(f"Password: Admin123!")
            print("=" * 40)
            print("\nYou can now use these credentials to log in to the admin dashboard.")
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Error creating admin user: {e}")
            return False
    
    return True

def init_database():
    """Initialize the database with all tables."""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("SUCCESS: Database tables created successfully!")
            return True
        except Exception as e:
            print(f"ERROR: Error creating database tables: {e}")
            return False

if __name__ == '__main__':
    print("Healthcare Management System - Admin Setup")
    print("=" * 50)
    
    # Initialize database
    print("\n1. Initializing database...")
    if not init_database():
        sys.exit(1)
    
    # Create admin user
    print("\n2. Creating admin user...")
    if not create_admin():
        sys.exit(1)
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Start the backend server: python run.py")
    print("2. Start the frontend: streamlit run app.py")
    print("3. Use the admin credentials to log in")