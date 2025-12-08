from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from app.routes import auth, complaints, admin, home, user, contact     
from app.db import query
from app.user_wrapper import UserWrapper
from app.extensions import bcrypt, mail
import os


load_dotenv()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    upload_path = os.path.join(app.root_path, "static", "uploads")
    app.config["UPLOAD_FOLDER"] = upload_path
    os.makedirs(upload_path, exist_ok=True)

    @login_manager.user_loader
    def load_user(user_id):
        admin = query(
            "SELECT admin_id, admin_name AS name, email FROM admins WHERE admin_id = %s",
            (user_id,),
            fetchone=True,
        )
        if admin:
            return UserWrapper(admin["admin_id"], admin["name"], admin["email"], True)

        user = query(
            "SELECT user_id, username AS name, email FROM users WHERE user_id = %s",
            (user_id,),
            fetchone=True,
        )
        if user:
            return UserWrapper(user["user_id"], user["name"], user["email"], False)

        return None

    for bp in (auth.bp, complaints.bp, admin.bp, home.bp, user.bp, contact.bp):
        app.register_blueprint(bp)

    return app
