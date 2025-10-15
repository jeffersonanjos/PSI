from flask_login import LoginManager
from flask_bcrypt import Bcrypt

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
# Mensagem de login em português e categoria de alerta amigável
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

# Password hashing
bcrypt = Bcrypt()
