from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import timedelta
from app.db import query

bp = Blueprint("user", __name__, url_prefix="/user")


# -----------------------------
#        USER DASHBOARD
# -----------------------------
@bp.route("/")
@login_required
def user_dashboard():
    user = query(
        "SELECT username, email, last_login FROM users WHERE user_id = %s",
        (current_user.id,),
        fetchone=True
    )

    status = request.args.get("status")

    if status:
        rows = query(
            """
            SELECT c.*, d.department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.user_id
            JOIN departments d ON d.department_id = c.department_id
            WHERE c.status = %s and c.user_id = %s
            ORDER BY c.created_at DESC
            """,
            (status, current_user.id,),
            fetchall=True
        )

    else:
        rows = query(
            """
            SELECT c.*, d.department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.user_id
            JOIN departments d ON d.department_id = c.department_id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
            """,
            (current_user.id,),
            fetchall=True
        )

    total = query(
        "SELECT count(*) FROM complaints WHERE user_id = %s",
        (current_user.id,),
        fetchone=True
    )[0]

    for c in rows:
        c["created_at"] = (c["created_at"] + timedelta(hours=5, minutes=30))\
                            .strftime("%H:%M | %d %B %Y")

        if c["assigned_at"]:
            c["assigned_at"] = (c["assigned_at"] + timedelta(hours=5, minutes=30))\
                            .strftime("%d %B %Y")
        else:
            c["assigned_at"] = ""

    if user["last_login"]:
        user["last_login"] = (user["last_login"] + timedelta(hours=5, minutes=30))\
                        .strftime("%H:%M  |  %d-%B-%Y")

    return render_template("user_dashboard.html", complaints=rows, user=user, status=status, total=total)
