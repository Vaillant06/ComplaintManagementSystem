from flask import Blueprint, render_template, flash

bp = Blueprint("contact", __name__, url_prefix="/contact")

@bp.route("/")
def contact_us():
    return render_template("contact_us.html")


@bp.route("/contact_info", methods=["GET", "POST"])
def message():
    flash("Thank you for contacting us. We will respond you soon!", "success")
    return render_template("contact_us.html")
