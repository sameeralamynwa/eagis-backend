from wtforms import StringField, validators
from wtforms.widgets import PasswordInput
from core.wt_forms import BaseForm


class LoginForm(BaseForm):
    username = StringField(
        "Username :",
        validators=[validators.DataRequired(), validators.length(min=1)],
    )
    password = StringField(
        "Password", widget=PasswordInput(), validators=[validators.DataRequired()]
    )
