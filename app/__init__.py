from flask import Flask, redirect
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app.db import query
    from app.user_wrapper import UserWrapper

    @login_manager.user_loader
    def load_user(user_id):
        user = query("SELECT * FROM users WHERE id=%s", (user_id,), fetchone=True)
        if user:
            return UserWrapper(user["id"], user["name"], user["email"], user["role"])
        return None

    from app.routes import auth, complaints, admin, home, user, contact
    app.register_blueprint(auth.bp)
    app.register_blueprint(complaints.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(contact.bp)

    return app
