from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_mail import Mail
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

load_dotenv()
mail = Mail()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    mail.init_app(app)

    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app.db import query
    from app.user_wrapper import UserWrapper

    @login_manager.user_loader
    def load_user(user_id):

        admin = query(
            "SELECT admin_id, admin_name, email FROM admins WHERE admin_id=%s",
            (user_id,), fetchone=True
        )
        if admin:
            return UserWrapper(
                admin["admin_id"],
                admin["admin_name"],
                admin["email"],
                True
            )

        user = query(
            "SELECT user_id, username, email FROM users WHERE user_id=%s",
            (user_id,), fetchone=True
        )
        if user:
            return UserWrapper(
                user["user_id"],                    
                user["username"],
                user["email"],
                False
            )

        return None

    from app.routes import auth, complaints, admin, home, user, contact

    app.register_blueprint(auth.bp)
    app.register_blueprint(complaints.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(contact.bp)

    return app
