from Acquisition import aq_inner
from plone import api
from plone.app.contenttypes.browser.collection import CollectionView
from plone.app.contenttypes.browser.folder import FolderView
from plone.dexterity.browser.view import DefaultView
from plone.memoize.view import memoize


class GridListingBase(DefaultView):

    def get_default(self, attr):
        context = aq_inner(self.context)
        val = getattr(context, attr, None)
        if val is None:
            if attr in self.w:
                # return widgets default attribute adapter
                return self.w[attr].value
            return
        return val

    @property
    def show_about(self):
        # use registry setting even if not anonymous
        return api.portal.get_registry_record(
            "plone.allow_anon_views_about", default=False
        )

    @memoize
    def get_thumb_scale_summary(self):
        if getattr(self.context, "suppress_thumbs", False):
            return None
        thsize = getattr(self.context, "thumb_scale_summary", None)
        if thsize:
            return thsize
        if api.portal.get_registry_record("plone.no_thumbs_summary", default=False):
            return None
        return self.get_default("preview_scale")


class FolderGridListing(GridListingBase, FolderView):
    pass


class CollectionGridListing(GridListingBase, CollectionView):
    pass
