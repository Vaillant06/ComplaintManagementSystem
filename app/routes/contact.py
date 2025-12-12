from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user
from app.db import query 

bp = Blueprint("contact", __name__, url_prefix="/contact")


# -----------------------------
#          CONTACT US
# -----------------------------
@bp.route("/")
def contact_us():
    return render_template("contact_us.html")


# -----------------------------
#            MESSAGE
# -----------------------------
@bp.route("/contact_info", methods=["GET", "POST"])
def message():
    if request.method == "POST":
        name  = request.form["name"]
        email = request.form["email"]
        rating = request.form["rating"]
        message = request.form["message"]

        query(
            '''
            INSERT INTO user_review(name, email, rating, user_message, created_at)
            values(%s, %s, %s, %s, NOW())
            ''',
            (name, email, rating, message),
            commit=True
        )

        flash("Thank you for contacting us. We will respond to you soon!", "success")

        if current_user.is_authenticated:   
            return redirect(url_for("user.user_dashboard"))

        else:
            return redirect(url_for("home.home"))
    
    return render_template("contact_us.html")
