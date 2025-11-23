from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.db import query
from app import bcrypt
from app.user_wrapper import UserWrapper
from datetime import datetime

bp = Blueprint("auth", __name__, url_prefix="/auth")


# -----------------------------
#           REGISTER
# -----------------------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match", "alert")
            return render_template("register.html")

        existing_email = query("select * from users where email=%s", (email,), fetchone=True)
        if existing_email:
            flash("Email exists already", "alert")
            return render_template("register.html")

        hashed_password = bcrypt.generate_password_hash(password).decode()

        query(
            "insert into users(username, email, password) values (%s, %s, %s)",
            (name, email, hashed_password),
            commit=True
        )

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# -----------------------------
#            LOGIN
# -----------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = query("SELECT * FROM users WHERE email=%s", (email,), fetchone=True)
        if user and bcrypt.check_password_hash(user["password"], password):

            query(
                "UPDATE users SET last_login = NOW() WHERE user_id = %s",
                (user["user_id"],),
                commit=True,
            )

            user_obj = UserWrapper(
                user["user_id"], user["username"], user["email"], False
            )
            login_user(user_obj)
            return redirect(url_for("user.user_dashboard"))

        admin = query("SELECT * FROM admins WHERE email=%s", (email,), fetchone=True)
        if admin and bcrypt.check_password_hash(admin["password"], password):

            query(
                "UPDATE admins SET last_login = NOW() WHERE admin_id = %s",
                (admin["admin_id"],),
                commit=True,
            )

            user_obj = UserWrapper(
                admin["admin_id"], admin["admin_name"], admin["email"], True
            )
            login_user(user_obj)
            return redirect(url_for("admin.admin_home"))

        flash("Invalid credentials!", "alert")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


# -----------------------------
#            LOGOUT
# -----------------------------
@bp.route("/logout")
@login_required
def logout():
    flash("Logout successful!", "success")
    logout_user()

    return redirect(url_for("auth.login"))
