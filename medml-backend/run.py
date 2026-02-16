import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Start the application factory

from app import create_app

# Get the config name from environment or use 'default'
config_name = os.getenv('FLASK_ENV', 'default')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True)