from flask import Blueprint, render_template, flash, request
from flask_login import login_required, current_user
from datetime import timedelta
from app.db import query

bp = Blueprint("user", __name__, url_prefix="/user")

@bp.route("/")
@login_required
def user_dashboard():
    user = query(
        "SELECT * FROM users WHERE id=%s",
        (current_user.id,),
        fetchone=True
    )

    status = request.args.get("status")

    if status:
        rows = query(
            """
            SELECT c.*, u.name AS user_name, d.name AS department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            JOIN departments d ON d.id = c.department_id
            WHERE c.status = %s and c.user_id = %s
            ORDER BY c.created_at DESC
            """,
            (status, current_user.id,),
            fetchall=True
        )

    else:
        rows = query(
            """
            SELECT c.*, u.name AS user_name, d.name AS department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            JOIN departments d ON d.id = c.department_id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
            """,
            (current_user.id,),
            fetchall=True
        )

    for c in rows:
        c["created_at"] = (c["created_at"] + timedelta(hours=5, minutes=30))\
                            .strftime("%H:%M | %d-%m-%Y")

    if user["last_login"]:
        user["last_login"] = (user["last_login"] + timedelta(hours=5, minutes=30))\
                        .strftime("%H:%M  |  %d-%m-%Y")
    
    return render_template("user_dashboard.html", complaints=rows, user=user, status=status)