from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.db import query
from app import bcrypt
from app.user_wrapper import UserWrapper

bp = Blueprint("auth", __name__, url_prefix="/auth")


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
            "insert into users(name, email, password, role) values (%s %s %s)",
            (name, email, hashed_password),
            commit=True
        )

        return redirect(url_for("auth.login"))
    
    return render_template("register.html")

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

        flash("Invalid credentials!", "alert")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    logout_user()
    flash("Admin Logout Successful!", "success")
    return redirect(url_for("auth.login"))