"""Routes for the Leaderboard tab"""

from flask import Blueprint, render_template
from flask_login import current_user, login_required

import db

from leaderboard.forms import LeaderboardForm

leaderboard_bp = Blueprint("leaderboard", __name__, template_folder="templates")


@leaderboard_bp.route("/leaderboard", methods=["GET", "POST"])
@login_required
def leaderboard():
    """This endpoint allows a user to see the leaderboard and submit flags"""

    user_id = current_user.user_id
    form = LeaderboardForm()
    notification = None
    conn = db.get_connection()

    if form.validate_on_submit():
        # check to see if it's a valid flag
        flag = form.flag.data
        flag_row = db.get_flag(conn, flag)
        if flag_row:
            # check to see if it's already been captured
            captured_flags_list = db.get_captured_flags(conn, user_id)
            already_captured = False
            for captured_flag in captured_flags_list:
                if flag == captured_flag["flag_id"]:
                    already_captured = True
                    form.flag.errors.append("Flag already captured")
                    break
            if not already_captured:
                # capture the flag
                db.capture_flag(conn, user_id, flag)
                conn.commit()
                notification = (
                    f"Congratulations, you captured the flag for {flag_row['name']}!"
                )
                form = LeaderboardForm(formdata=None)
        else:
            form.flag.errors.append("Invalid flag")

    leaderboard_data = db.get_leaderboard(conn)

    return render_template(
        "leaderboard.html",
        form=form,
        notification=notification,
        leaderboard=leaderboard_data,
    )
