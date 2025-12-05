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

    ITEMS_PER_PAGE = 10
    
    status = request.args.get("status")

    page = request.args.get("page", 1, type=int)
    offset = (page - 1) * ITEMS_PER_PAGE

    total = query("SELECT COUNT(*) FROM complaints", fetchone=True)[0]
    total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    if status:
        rows = query(
            """
            SELECT c.*, d.department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.user_id
            JOIN departments d ON d.department_id = c.department_id
            WHERE c.status = %s and c.user_id = %s
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (status, current_user.id, ITEMS_PER_PAGE, offset),
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
            LIMIT %s OFFSET %s
            """,
            (current_user.id, ITEMS_PER_PAGE, offset),
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

    return render_template("user_dashboard.html", complaints=rows, user=user, status=status, total=total, total_pages=total_pages, page=page)
