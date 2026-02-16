#!/usr/bin/env python3
"""
Script to clear Flask-Limiter cache
Run this if you're getting rate limit errors during development
"""

from app import create_app
from app.extensions import limiter

def clear_rate_limits():
    """Clear all rate limit data"""
    app = create_app()
    with app.app_context():
        try:
            # Clear the limiter's storage
            limiter.storage.clear()
            print("✅ Rate limit cache cleared successfully!")
        except Exception as e:
            print(f"❌ Error clearing rate limits: {e}")

if __name__ == "__main__":
    clear_rate_limits()
