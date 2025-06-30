from wtforms import SelectField, StringField, validators, IntegerField, widgets
from core.dtos import PaginationQuery
from core.wt_forms import BaseForm


class BlogsListQuery(PaginationQuery):
    search: str | None = None


class DeleteBlogForm(BaseForm):
    pass


class CreateBlogForm(BaseForm):
    slug = StringField(
        "Slug :",
        validators=[
            validators.DataRequired(),
            validators.length(min=5),
            validators.regexp(
                r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
                message="""Slug can only contain lowercase letters, numbers,
                  and hyphens (no leading/trailing or consecutive hyphens).""",
            ),
        ],
    )
    title = StringField(
        "Title :",
        validators=[validators.DataRequired(), validators.length(min=2)],
    )
    category_id = SelectField(
        "Category",
        validators=[validators.optional()],
        coerce=int,
    )
    thumbnail_id = IntegerField(
        "Thumbnail :", validators=[validators.optional()], widget=widgets.NumberInput()
    )
    short_desc = StringField(
        "Short Description :",
        validators=[validators.optional()],
    )
    content = StringField("Content:", validators=[validators.optional()])
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
