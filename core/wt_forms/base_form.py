from datetime import timedelta
from wtforms import Form
from wtforms.csrf.session import SessionCSRF
from core import get_config


config = get_config()


class BaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = config.jwt_secrete.encode()
        csrf_time_limit = timedelta(minutes=20)
