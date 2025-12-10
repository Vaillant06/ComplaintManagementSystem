from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.db import query
from app.extensions import bcrypt 
from app.user_wrapper import UserWrapper
import re

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not name or not email or not password:
            flash("All fields are required!", "alert")
            return redirect(url_for("auth.register"))

        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{7,}$"
        if not re.match(pattern, password):
            flash("Password should contain one upper case, one lower case, numbers and special characters", "alert")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match!", "alert")
            return redirect(url_for("auth.register"))

        existing_email = query(
            "SELECT 1 FROM users WHERE email=%s", (email,), fetchone=True
        )
        if existing_email:
            flash("Email already exists!", "alert")
            return redirect(url_for("auth.register"))

        hashed_password = bcrypt.generate_password_hash(password).decode()

        query(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password),
            commit=True,
        )

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        admin = query("SELECT * FROM admins WHERE email=%s", (email,), fetchone=True)
        if admin and bcrypt.check_password_hash(admin["password"], password):

            query(
                "UPDATE admins SET last_login = NOW() WHERE admin_id = %s",
                (admin["admin_id"],),
                commit=True
            )

            login_user(
                UserWrapper(
                    admin["admin_id"], admin["admin_name"], admin["email"], "admin"
                )
            )

            return redirect(url_for("admin.admin_home"))


        staff = query("SELECT * FROM staff WHERE email=%s", (email,), fetchone=True)
        print(staff["password"])
        if staff and staff["password"] == password:
            query(
                "UPDATE staff SET last_login = NOW() WHERE staff_id = %s",
                (staff["staff_id"],),
                commit=True
            )

            login_user(
                UserWrapper(
                    staff["staff_id"], staff["staff_name"], staff["email"], "staff"
                )
            )

            return redirect(url_for("staff.staff_dashboard"))


        user = query("SELECT * FROM users WHERE email=%s", (email,), fetchone=True)
        if user and bcrypt.check_password_hash(user["password"], password):

            query(
                "UPDATE users SET last_login = NOW() WHERE user_id = %s",
                (user["user_id"],),
                commit=True
            )

            login_user(
                UserWrapper(
                    user["user_id"], user["username"], user["email"], "user"
                )
            )

            return redirect(url_for("user.user_dashboard"))

        flash("Invalid credentials!", "alert")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
