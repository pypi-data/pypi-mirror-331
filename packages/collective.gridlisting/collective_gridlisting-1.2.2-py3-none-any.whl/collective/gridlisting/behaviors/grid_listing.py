from collective.gridlisting import _
from plone import api
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.base.utils import safe_hasattr
from plone.supermodel import directives
from plone.supermodel import model
from z3c.form.interfaces import IValue
from z3c.form.interfaces import NO_VALUE
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


class IGridListingMarker(Interface):
    pass


@provider(IFormFieldProvider)
class IGridListing(model.Schema):
    """ """

    row_css_class = schema.TextLine(
        title=_("Container row"),
        description=_("eg. if you want to set gutter between columns define here."),
        required=False,
        default="",
        missing_value="",
        # the combination of default and missing_value with the same value
        # triggers the DefaultValueAdapter below
    )

    column_css_class = schema.TextLine(
        title=_("Column"),
        description=_(
            "Use grid css class combinations for column. Example: 'col-12 col-md-6 col-xl-3'"
        ),
        required=False,
        default="",
        missing_value="",
    )

    column_content_css_class = schema.TextLine(
        title=_("Column content"),
        description=_(
            "If you want borders or backgrounds inside the column define it here."
        ),
        required=False,
        default="row",
        missing_value="row",
    )

    column_content_text_css_class = schema.TextLine(
        title=_("Column content text"),
        description=_("CSS class(es) for title/description/link in column content"),
        required=False,
        default="col",
        missing_value="col",
    )

    column_content_image_css_class = schema.TextLine(
        title=_("Column content image"),
        description=_("CSS class(es) for preview image in column content"),
        required=False,
        default="col-3 text-end",
        missing_value="col-3 text-end",
    )

    item_title_tag = schema.Choice(
        title=_("Listing item title tag"),
        vocabulary="collective.gridlisting.listing_title_tags",
        default="h3",
    )

    preview_scale = schema.Choice(
        title=_("Preview image scale"),
        vocabulary="plone.app.vocabularies.ImagesScales",
        default="preview",
    )

    crop_preview = schema.Bool(
        title=_("Crop preview image to scale"),
        required=False,
        default=False,
    )

    enable_masonry = schema.Bool(
        title=_("Enable masonry layout"),
        description=_("See masonry documentation."),
        required=False,
        default=False,
        missing_value=False,
    )

    masonry_options = schema.TextLine(
        title=_("Additional masonry options"),
        description=_(
            'Options for "pat-masonry" see https://patternslib.com/demos/masonry.'
        ),
        required=False,
        default="",
        missing_value="",
    )

    show_more_link = schema.Bool(
        title=_("Show more link"),
        description=_(
            "Show a separate link to the item below the description/title with the given text below. "
            "If deactivated, the item tile is used as link."
        ),
        required=False,
        default=False,
    )

    more_link_text = schema.TextLine(
        title=_("Text for 'more' link below title/description"),
        required=False,
        default="more",
        missing_value="more",
    )

    directives.fieldset(
        "gridlisting",
        label=_("Grid listing"),
        description=_(
            "Define grid listing properties. For further information see https://getbootstrap.com/docs/5.3/layout/grid/"
        ),
        fields=[
            "row_css_class",
            "column_css_class",
            "column_content_css_class",
            "column_content_text_css_class",
            "column_content_image_css_class",
            "item_title_tag",
            "preview_scale",
            "crop_preview",
            "enable_masonry",
            "masonry_options",
            "show_more_link",
            "more_link_text",
        ],
    )


@implementer(IValue)
class DefaultSettingsValue:
    # get default values from registry
    # see ???

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.field = field
        self.form = form
        self.widget = widget

    def get(self):
        if "IGridListing" not in self.widget.name:
            # only lookup our behavior fields
            return NO_VALUE
        return (
            api.portal.get_registry_record(
                f"collective.gridlisting.{self.field.__name__}",
                default=NO_VALUE,
            )
            or NO_VALUE
        )


@implementer(IGridListing)
@adapter(IGridListingMarker)
class GridListing:
    def __init__(self, context):
        self.context = context

    @property
    def row_css_class(self):
        if safe_hasattr(self.context, "row_css_class"):
            return self.context.row_css_class
        return None

    @row_css_class.setter
    def row_css_class(self, value):
        self.context.row_css_class = value

    @property
    def column_css_class(self):
        if safe_hasattr(self.context, "column_css_class"):
            return self.context.column_css_class
        return None

    @column_css_class.setter
    def column_css_class(self, value):
        self.context.column_css_class = value

    @property
    def column_content_css_class(self):
        if safe_hasattr(self.context, "column_content_css_class"):
            return self.context.column_content_css_class
        return None

    @column_content_css_class.setter
    def column_content_css_class(self, value):
        self.context.column_content_css_class = value

    @property
    def column_content_text_css_class(self):
        if safe_hasattr(self.context, "column_content_text_css_class"):
            return self.context.column_content_text_css_class
        return None

    @column_content_text_css_class.setter
    def column_content_text_css_class(self, value):
        self.context.column_content_text_css_class = value

    @property
    def column_content_image_css_class(self):
        if safe_hasattr(self.context, "column_content_image_css_class"):
            return self.context.column_content_image_css_class
        return None

    @column_content_image_css_class.setter
    def column_content_image_css_class(self, value):
        self.context.column_content_image_css_class = value

    @property
    def item_title_tag(self):
        if safe_hasattr(self.context, "item_title_tag"):
            return self.context.item_title_tag
        return None

    @item_title_tag.setter
    def item_title_tag(self, value):
        self.context.item_title_tag = value

    @property
    def preview_scale(self):
        if safe_hasattr(self.context, "preview_scale"):
            return self.context.preview_scale
        return None

    @preview_scale.setter
    def preview_scale(self, value):
        self.context.preview_scale = value

    @property
    def crop_preview(self):
        if safe_hasattr(self.context, "crop_preview"):
            return self.context.crop_preview
        return None

    @crop_preview.setter
    def crop_preview(self, value):
        self.context.crop_preview = value

    @property
    def enable_masonry(self):
        if safe_hasattr(self.context, "enable_masonry"):
            return self.context.enable_masonry
        return None

    @enable_masonry.setter
    def enable_masonry(self, value):
        self.context.enable_masonry = value

    @property
    def masonry_options(self):
        if safe_hasattr(self.context, "masonry_options"):
            return self.context.masonry_options
        return None

    @masonry_options.setter
    def masonry_options(self, value):
        self.context.masonry_options = value

    @property
    def show_more_link(self):
        if safe_hasattr(self.context, "show_more_link"):
            return self.context.show_more_link
        return None

    @show_more_link.setter
    def show_more_link(self, value):
        self.context.show_more_link = value

    @property
    def more_link_text(self):
        if safe_hasattr(self.context, "more_link_text"):
            return self.context.more_link_text
        return None

    @more_link_text.setter
    def more_link_text(self, value):
        self.context.more_link_text = value
