from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from app.db import query

bp = Blueprint("user", __name__, url_prefix="/user")

@bp.route("/")
@login_required
def user_dashboard():
    rows = query(
        "select * from complaints where user_id=%s order by created_at desc",
        (current_user.id,),
        fetchall = True
    )
    
    flash("Login Successful", "success")
    return render_template("user_dashboard.html", complaints=rows )