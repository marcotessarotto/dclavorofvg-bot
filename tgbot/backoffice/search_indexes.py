import datetime
from haystack import indexes

from backoffice.models import NewsItem

# https://django-haystack.readthedocs.io/en/master/searchindex_api.html#quick-start


class NewsItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False) # use_template=True tells Haystack to use a template

    title = indexes.CharField(model_attr='title')
    news_text = indexes.CharField(model_attr='text')

    updated_at = indexes.DateTimeField(model_attr='updated_at')

    def get_model(self):
        return NewsItem

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(updated_at__lte=datetime.datetime.now())

