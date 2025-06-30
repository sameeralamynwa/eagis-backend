from wtforms import StringField, validators, IntegerField, widgets
from core.dtos import PaginationQuery
from core.wt_forms import BaseForm


class BlogCategorysListQuery(PaginationQuery):
    search: str | None = None


class DeleteBlogCategoryForm(BaseForm):
    pass


class CreateBlogCategoryForm(BaseForm):
    slug = StringField(
        "Slug :",
        validators=[
            validators.DataRequired(),
            validators.length(min=2),
            validators.regexp(
                r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
                message="""Slug can only contain lowercase letters, numbers,
                  and hyphens (no leading/trailing or consecutive hyphens).""",
            ),
        ],
    )
    name = StringField(
        "Name :",
        validators=[validators.DataRequired(), validators.length(min=2)],
    )
    thumbnail_id = IntegerField(
        "Thumbnail :", validators=[validators.optional()], widget=widgets.NumberInput()
    )
    short_desc = StringField(
        "Short Description :",
        validators=[validators.optional()],
    )
    meta_title = StringField(
        "Meta Title :",
        validators=[validators.optional()],
    )
    meta_keywords = StringField(
        "Meta Keywords :",
        validators=[validators.optional()],
    )
    meta_desc = StringField(
        "Meta Description :",
        validators=[validators.optional()],
    )
