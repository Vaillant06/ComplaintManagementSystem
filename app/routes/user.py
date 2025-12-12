from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import timedelta
from app.db import query

bp = Blueprint("user", __name__, url_prefix="/user")

IST = timedelta(hours=5, minutes=30)


def to_ist(dt, pattern="%H:%M | %d %B %Y"):
    return (dt + IST).strftime(pattern) if dt else None


@bp.route("/")
@login_required
def user_dashboard():

    user = query(
        "SELECT username, email, last_login FROM users WHERE user_id=%s",
        (current_user.id,),
        fetchone=True,
    )

    ITEMS_PER_PAGE = 10
    status = request.args.get("status")  # Filter by complaint status
    page = request.args.get("page", 1, type=int)
    offset = (page - 1) * ITEMS_PER_PAGE

    # -----------------------------
    #  Total count
    # -----------------------------
    if status:
        total_count = query(
            """
            SELECT COUNT(*)
            FROM complaints c
            WHERE c.status=%s AND c.user_id=%s
            """,
            (status, current_user.id),
            fetchone=True,
        )[0]
    else:
        total_count = query(
            "SELECT COUNT(*) FROM complaints WHERE user_id=%s",
            (current_user.id,),
            fetchone=True,
        )[0]

    total_pages = (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    # -----------------------------
    #  Fetch complaints
    # -----------------------------
    if status:
        rows = query(
            """
            SELECT c.*, u.username, d.department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.user_id
            JOIN departments d ON d.department_id = c.department_id
            WHERE c.status=%s AND c.user_id=%s
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (status, current_user.id, ITEMS_PER_PAGE, offset),
            fetchall=True,
        )
    else:
        rows = query(
            """
            SELECT c.*, u.username, d.department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.user_id
            JOIN departments d ON d.department_id = c.department_id
            WHERE c.user_id=%s
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (current_user.id, ITEMS_PER_PAGE, offset),
            fetchall=True,
        )

    # Total overall complaints for this user
    total = query(
        "SELECT COUNT(*) FROM complaints WHERE user_id=%s",
        (current_user.id,),
        fetchone=True,
    )[0]

    # -----------------------------
    #  Format timestamps
    # -----------------------------
    for c in rows:
        c["created_at"] = to_ist(c["created_at"])

        if c.get("assigned_at"):
            c["assigned_at"] = to_ist(c["assigned_at"], "%d %B %Y")

        if c.get("resolved_at"):
            c["resolved_at"] = to_ist(c["resolved_at"], "%d %B %Y")

    # Format last login
    if user.get("last_login"):
        user["last_login"] = to_ist(user["last_login"], "%H:%M | %d-%B-%Y")

    return render_template(
        "user_dashboard.html",
        complaints=rows,
        user=user,
        status=status,
        total=total,
        total_pages=total_pages,
        page=page,
    )
