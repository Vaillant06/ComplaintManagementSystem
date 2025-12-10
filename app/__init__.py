from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from app.routes import auth, complaints, admin, staff, home, user, contact     
from app.db import query
from app.user_wrapper import UserWrapper
from app.extensions import bcrypt, mail
import os


load_dotenv()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize extensions
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Upload folder
    upload_path = os.path.join(app.root_path, "static", "uploads")
    app.config["UPLOAD_FOLDER"] = upload_path
    os.makedirs(upload_path, exist_ok=True)

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        if user_id.startswith(("E", "W", "P", "H")):  
            staff = query(
                "SELECT staff_id, staff_name, email FROM staff WHERE staff_id=%s",
                (user_id,),
                fetchone=True
            )
            if staff:
                return UserWrapper(staff["staff_id"], staff["staff_name"], staff["email"], "staff")

        if user_id.isdigit():
            admin = query(
                "SELECT admin_id, admin_name, email FROM admins WHERE admin_id=%s",
                (user_id,),
                fetchone=True
            )
            if admin:
                return UserWrapper(admin["admin_id"], admin["admin_name"], admin["email"], "admin")

            user = query(
                "SELECT user_id, username, email FROM users WHERE user_id=%s",
                (user_id,),
                fetchone=True
            )
            if user:
                return UserWrapper(user["user_id"], user["username"], user["email"], "user")

        return None


    for bp in (auth.bp, complaints.bp, admin.bp, staff.bp, home.bp, user.bp, contact.bp):
        app.register_blueprint(bp)

    return app
