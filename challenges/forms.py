"""Form used by the challenges"""

from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField

class ChallengeForm(FlaskForm):
    """Basic form for submitting a flag"""

    flag = StringField("Flag")
    capture = SubmitField("Capture")
    stop = SubmitField("Stop this Challenge")
