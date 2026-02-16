import mongoengine as me
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

class MongoEngineShim:
    def __init__(self, app=None):
        self.Document = me.Document
        self.DynamicDocument = me.DynamicDocument
        self.EmbeddedDocument = me.EmbeddedDocument
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        config = app.config.get('MONGODB_SETTINGS', {})
        # If host is provided in MONGODB_SETTINGS, use it
        host = config.get('host') or config.get('db_url')
        if host:
             me.connect(host=host)
        else:
             # Default to local if no config found
             me.connect(db='medml', host='mongodb://localhost:27017/medml')

db = MongoEngineShim()
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()

# --- ADDED: Rate Limiter ---
# Use get_remote_address as the key function
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour", "50 per minute"],
    storage_uri="memory://"  # Use in-memory storage for development
)