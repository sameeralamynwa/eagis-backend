from wtforms import (
    StringField,
    validators,
)
from core.dtos import PaginationQuery
from apps.auth.enums import Permissions
from core.wt_forms import BaseForm, custom_fields


class RolesListQuery(PaginationQuery):
    search: str | None = None


class DeleteRoleForm(BaseForm):
    pass


class CreateRoleForm(BaseForm):
    name = StringField(
        "Name :",
        validators=[validators.DataRequired(), validators.length(min=5)],
    )
    permissions = custom_fields.MultiCheckboxField(
        "Permissions",
        choices=[(type.value, type.value) for type in Permissions],
        coerce=Permissions,
    )
