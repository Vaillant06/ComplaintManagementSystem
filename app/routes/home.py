from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint("home", __name__)

@bp.route("/")
def home():
    return render_template("landing_page.html")