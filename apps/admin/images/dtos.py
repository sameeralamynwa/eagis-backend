from wtforms import (
    StringField,
    validators,
)
from core.dtos import PaginationQuery
from core.wt_forms import BaseForm


class ImagesListQuery(PaginationQuery):
    search: str | None = None


class DeleteImageForm(BaseForm):
    pass


class CreateImageForm(BaseForm):
    title = StringField(
        "Title :",
        validators=[validators.DataRequired(), validators.length(min=2)],
    )
    alt_text = StringField(
        "Alt Texts :",
        validators=[validators.DataRequired(), validators.length(min=2)],
    )
