from horhor.models.page_models import CoderedPage
from modelcluster.fields import ParentalKey
from horhor.forms import CoderedFormField
from horhor.models import (
    CoderedArticlePage,
    CoderedArticleIndexPage,
    CoderedEventIndexPage,
    CoderedEventPage,
    CoderedEventOccurrence,
    CoderedEmail,
    CoderedFormPage,
    CoderedLocationIndexPage,
    CoderedLocationPage,
    CoderedStreamFormPage,
    CoderedWebPage,
)


class ArticlePage(CoderedArticlePage):
    class Meta:
        verbose_name = "Article"
        ordering = [
            "-first_published_at",
        ]

    # Only allow this page to be created beneath an ArticleIndexPage.
    parent_page_types = ["testapp.ArticleIndexPage"]

    template = "horhor/pages/article_page.html"
    search_template = "horhor/pages/article_page.search.html"


class ArticleIndexPage(CoderedArticleIndexPage):
    class Meta:
        verbose_name = "Article Landing Page"

    index_order_by_default = ""

    # Override to specify custom index ordering choice/default.
    index_query_pagemodel = "testapp.ArticlePage"

    # Only allow ArticlePages beneath this page.
    subpage_types = ["testapp.ArticlePage"]

    template = "horhor/pages/article_index_page.html"


class FormPage(CoderedFormPage):
    class Meta:
        verbose_name = "Form"

    template = "horhor/pages/form_page.html"


class FormPageField(CoderedFormField):
    class Meta:
        ordering = ["sort_order"]

    page = ParentalKey("FormPage", related_name="form_fields")


class FormConfirmEmail(CoderedEmail):
    page = ParentalKey("FormPage", related_name="confirmation_emails")


class WebPage(CoderedWebPage):
    class Meta:
        verbose_name = "Web Page"

    template = "horhor/pages/web_page.html"


class EventPage(CoderedEventPage):
    class Meta:
        verbose_name = "Event Page"

    parent_page_types = ["testapp.EventIndexPage"]
    subpage_types = []
    template = "horhor/pages/event_page.html"


class EventIndexPage(CoderedEventIndexPage):
    class Meta:
        verbose_name = "Events Landing Page"

    index_query_pagemodel = "testapp.EventPage"
    index_order_by_default = ""

    # Only allow EventPages beneath this page.
    subpage_types = ["testapp.EventPage"]

    template = "horhor/pages/event_index_page.html"


class EventOccurrence(CoderedEventOccurrence):
    event = ParentalKey(EventPage, related_name="occurrences")


class LocationPage(CoderedLocationPage):
    class Meta:
        verbose_name = "Location Page"

    template = "horhor/pages/location_page.html"

    # Only allow LocationIndexPages above this page.
    parent_page_types = ["testapp.LocationIndexPage"]


class LocationIndexPage(CoderedLocationIndexPage):
    class Meta:
        verbose_name = "Location Landing Page"

    # Override to specify custom index ordering choice/default.
    index_query_pagemodel = "testapp.LocationPage"

    # Only allow LocationPages beneath this page.
    subpage_types = ["testapp.LocationPage"]

    template = "horhor/pages/location_index_page.html"


class StreamFormPage(CoderedStreamFormPage):
    class Meta:
        verbose_name = "Stream Form"

    template = "horhor/pages/stream_form_page.html"


class StreamFormConfirmEmail(CoderedEmail):
    page = ParentalKey("StreamFormPage", related_name="confirmation_emails")


"""
--------------------------------------------------------------------------------
CUSTOM PAGE TYPES for testing specific features. These should be based on
CoderedPage when testing CoderedPage-specific functionality (which is where most
of our logic lives).
--------------------------------------------------------------------------------
"""


class IndexTestPage(CoderedPage):
    """
    Tests indexing features (show/sort/filter child pages).
    """

    class Meta:
        verbose_name = "Index Test Page"

    index_query_pagemodel = "testapp.WebPage"

    template = "horhor/pages/base.html"
