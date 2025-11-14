from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

bp = Blueprint("user", __name__, url_prefix="/user")

@bp.route("/")
@login_required
def user_dashboard():
    flash("Login Successful", "success")
    return render_template("user_dashboard.html")