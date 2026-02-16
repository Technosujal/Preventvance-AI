import os
import sys
from mongoengine import connect, disconnect

def test_connection():
    uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/medml')
    print(f"Attempting to connect to: {uri}")
    try:
        # disconnect any existing
        disconnect()
        # attempt connect
        client = connect(host=uri, serverSelectionTimeoutMS=2000)
        # trigger a command to verify
        client.admin.command('ping')
        print("Success: MongoDB is connected and responding.")
        return True
    except Exception as e:
        print(f"Error: Could not connect to MongoDB. {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        sys.exit(0)
    else:
        sys.exit(1)
