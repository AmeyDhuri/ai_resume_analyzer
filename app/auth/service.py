from app.extensions import db
from app.auth.models import User
from werkzeug.security import generate_password_hash, check_password_hash


def create_user(email, password):
    
    hashed_password = generate_password_hash(password)

    user = User(
        email=email,
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return user

def authenticate_user(email, password):

    user = User.query.filter_by(email=email).first()

    if not user:
        return None
    
    if not check_password_hash(user.password, password):
        return None
    
    return user