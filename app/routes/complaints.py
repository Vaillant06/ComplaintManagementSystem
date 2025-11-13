from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.db import query

bp = Blueprint("complaints", __name__, url_prefix="/complaints")

@bp.route("/")
@login_required
def list_complaints():
    rows = query(
        "SELECT * FROM complaints WHERE user_id=%s ORDER BY id DESC",
        (current_user.id,),
        fetchall=True
    )
    return render_template("complaints.html", complaints=rows)

@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_complaint():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        query(
            "INSERT INTO complaints (user_id, title, description) VALUES (%s, %s, %s)",
            (current_user.id, title, description),
            commit=True
        )

        return redirect(url_for("complaints.list_complaints"))

    return render_template("new_complaint.html")
