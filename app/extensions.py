from flask_login import LoginManager
from flask_bcrypt import Bcrypt

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Password hashing
bcrypt = Bcrypt()
