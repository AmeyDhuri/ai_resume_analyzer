from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class ChangePasswordForm(FlaskForm):

    current_password = PasswordField(
        "Current Password",
        validators=[
            DataRequired()
        ]
    )

    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )

    submit = SubmitField("Update Password")