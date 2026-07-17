from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman

db = SQLAlchemy()

migrate = Migrate()

jwt = JWTManager()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per day"]
)

csrf = CSRFProtect()

talisman = Talisman()