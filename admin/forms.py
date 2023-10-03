"""Forms used in system administration"""

from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    SubmitField,
    StringField,
    SelectField,
    IntegerField,
    HiddenField,
    validators,
)


class LoginForm(FlaskForm):
    """Form for a user to log in"""

    username = StringField("Username")
    password = PasswordField("Password")


class AddUserForm(FlaskForm):
    """Form for an admin to add a user"""

    username = StringField("Username")
    password = StringField("Password")
    role = SelectField("Role", choices=[(0, "Standard User"), (1, "Administrator")])


class ManageProfileForm(FlaskForm):
    """Form for a user to update their information"""

    password = PasswordField("Password", [validators.length(min=8)])
    update = SubmitField("Update")
    logout = SubmitField("Log Out")


class EditUserForm(FlaskForm):
    """Form for an admin to edit user information"""

    user_id = HiddenField()
    username = StringField("Username")
    password = StringField("Password")
    role = SelectField("Role", choices=[(0, "Standard User"), (1, "Administrator")])
    time_remaining = IntegerField("Time Remaining", validators=[validators.Optional()])
    update = SubmitField("Update")
    logout = SubmitField("Log Out")
    delete = SubmitField("Delete")
