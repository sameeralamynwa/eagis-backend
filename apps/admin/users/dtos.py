from wtforms import (
    SelectField,
    StringField,
    validators,
    BooleanField,
    SelectMultipleField,
)
from wtforms.widgets import EmailInput
from core.dtos import PaginationQuery
from apps.auth.enums import UserType
from core.wt_forms import BaseForm


class UserListQuery(PaginationQuery):
    search: str | None = None


class DeleteUserForm(BaseForm):
    pass


class CreateUserForm(BaseForm):
    name = StringField(
        "Name :",
        validators=[validators.DataRequired(), validators.length(min=5)],
    )
    username = StringField(
        "Username :",
        validators=[validators.DataRequired(), validators.length(min=5)],
    )
    email = StringField(
        "Email :",
        validators=[validators.DataRequired(), validators.email()],
        widget=EmailInput(),
    )
    password = StringField(
        "Password",
        validators=[validators.DataRequired(), validators.length(min=8)],
    )
    is_active = BooleanField(
        "Active?",
    )
    email_verified = BooleanField(
        "Email Verified?",
    )
    user_type = SelectField(
        "User Type",
        validators=[validators.DataRequired()],
        default=UserType.User.value,
        choices=[(type.value, type.name) for type in UserType],
    )
    role_ids = SelectMultipleField(
        "Roles", validators=[validators.optional()], coerce=int, render_kw={"size": 4}
    )

    def filter_email(self, field: str):
        return field.strip().lower() if field else field

    def filter_username(self, field: str):
        return field.strip().lower() if field else field


class UpdateUserForm(BaseForm):
    name = StringField(
        "Name :",
        validators=[validators.DataRequired(), validators.length(min=5)],
    )
    username = StringField(
        "Username :",
        validators=[validators.DataRequired(), validators.length(min=5)],
    )
    email = StringField(
        "Email :",
        validators=[validators.DataRequired(), validators.email()],
        widget=EmailInput(),
    )
    is_active = BooleanField(
        "Active?",
    )
    email_verified = BooleanField(
        "Email Verified?",
    )
    user_type = SelectField(
        "User Type",
        validators=[validators.DataRequired()],
        choices=[(type.value, type.name) for type in UserType],
        coerce=UserType,
    )
    role_ids = SelectMultipleField(
        "Roles", validators=[validators.optional()], coerce=int, render_kw={"size": 4}
    )

    def filter_email(self, field: str):
        return field.strip().lower() if field else field

    def filter_username(self, field: str):
        return field.strip().lower() if field else field
