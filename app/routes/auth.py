from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user
from app.db import query
from app import bcrypt
from app.user_wrapper import UserWrapper

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = query("SELECT * FROM users WHERE email=%s", (email,), fetchone=True)

        if user and bcrypt.check_password_hash(user["password"], password):
            user_obj = UserWrapper(user["id"], user["name"], user["email"], user["role"])
            login_user(user_obj)

            if user["role"] == "admin":
                return redirect(url_for("admin.admin_home"))
            else:
                return redirect(url_for("complaints.list_complaints"))

        return "Invalid credentials"

    return render_template("login.html")


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))