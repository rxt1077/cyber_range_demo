"""Routes for the Leaderboard tab"""

from flask import Blueprint, render_template
from flask_login import login_required

import db

leaderboard_bp = Blueprint("leaderboard", __name__, template_folder="templates")


@leaderboard_bp.route("/leaderboard", methods=["GET"])
@login_required
def leaderboard():
    """This endpoint allows a user to see the leaderboard"""

    conn = db.get_connection()

    leaderboard_data = db.get_leaderboard(conn)

    return render_template("leaderboard.html", leaderboard=leaderboard_data)
