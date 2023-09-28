"""The Leaderboard only has one basic form where you can submit a flag"""

from flask_wtf import FlaskForm
from wtforms import StringField


class LeaderboardForm(FlaskForm):
    """Basic form for submitting a flag"""

    flag = StringField("Flag")
