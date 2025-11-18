from flask import Blueprint, render_template

bp = Blueprint("home", __name__)


# -----------------------------
#     LANDING PAGE ROUTE
# -----------------------------
@bp.route("/")
def home():
    return render_template("landing_page.html")
