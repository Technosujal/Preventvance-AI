#!/usr/bin/env python3
"""
Simple database connection test script.
"""

import os
import sys
import sqlite3

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_database_connection():
    """Test direct database connection."""
    print("Testing database connection...")
    
    # Get the database path
    basedir = os.path.abspath(os.path.dirname(__file__))
    app_dir = os.path.join(basedir, 'app')
    db_path = os.path.join(app_dir, 'medml.db')
    
    print(f"Database path: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")
    
    try:
        # Test direct SQLite connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Tables found: {[table[0] for table in tables]}")
        
        # Test User table
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"Users in database: {user_count}")
        
        conn.close()
        print("SUCCESS: Database connection works!")
        return True
        
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False

def test_flask_app_connection():
    """Test Flask app database connection."""
    print("\nTesting Flask app database connection...")
    
    try:
        from app import create_app
        from app.models import db, User
        
        app = create_app('development')
        with app.app_context():
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("SUCCESS: Flask app database connection works!")
            
            # Test User query
            users = User.query.all()
            print(f"Users found via Flask: {len(users)}")
            
            return True
            
    except Exception as e:
        print(f"ERROR: Flask app database connection failed: {e}")
        return False

if __name__ == '__main__':
    print("Database Connection Test")
    print("=" * 30)
    
    # Test direct connection
    direct_ok = test_database_connection()
    
    # Test Flask app connection
    flask_ok = test_flask_app_connection()
    
    print("\n" + "=" * 30)
    print("Test Results:")
    print(f"Direct SQLite connection: {'PASS' if direct_ok else 'FAIL'}")
    print(f"Flask app connection: {'PASS' if flask_ok else 'FAIL'}")
    
    if direct_ok and flask_ok:
        print("\nSUCCESS: All database tests passed!")
    else:
        print("\nERROR: Some database tests failed!")
