from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, SelectField, IntegerField, HiddenField, validators

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')

class AddUserForm(FlaskForm):
    username = StringField('Username')
    password = StringField('Password')
    role = SelectField('Role', choices=[(0, "Standard User"), (1, "Administrator")])

class ManageProfileForm(FlaskForm):
    password = PasswordField('Password', [validators.length(min=8)])
    update = SubmitField('Update')
    logout = SubmitField('Log Out')

class EditUserForm(FlaskForm):
    user_id = HiddenField()
    username = StringField('Username')
    password = StringField('Password')
    role = SelectField('Role', choices=[(0, "Standard User"), (1, "Administrator")])
    time_remaining = IntegerField('Time Remaining', validators=[validators.Optional()])
    update = SubmitField('Update')
    logout = SubmitField('Log Out')
    delete = SubmitField('Delete')
