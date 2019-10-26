from app import db, User
from werkzeug.security import generate_password_hash

user = User(id = 0, username='username here', password_hash=generate_password_hash('password here', method='sha256'))
db.session.add(user)
db.session.commit()
