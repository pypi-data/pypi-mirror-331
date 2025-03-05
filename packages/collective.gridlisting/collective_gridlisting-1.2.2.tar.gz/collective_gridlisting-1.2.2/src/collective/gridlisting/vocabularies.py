from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


LISTING_TITLE_TAGS = (
    # H1 not allowed
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
)


@provider(IVocabularyFactory)
def listing_title_tags(context=None):
    return SimpleVocabulary.fromValues(LISTING_TITLE_TAGS)
