from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/")
def admin_home():
    return "Admin panel placeholder"
