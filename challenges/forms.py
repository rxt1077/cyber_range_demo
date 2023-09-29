from flask_wtf import FlaskForm
from wtforms import HiddenField

class StopChallengeForm(FlaskForm):
    url = HiddenField()
