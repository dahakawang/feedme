from rest_framework.serializers import *
from core_data.models import *
from rest_framework.utils.urls import replace_query_param


class ChildCollectionField(HyperlinkedRelatedField):
    def __init__(self, **kwargs):
        self.parent_id_name = kwargs.pop("parent_id_name")
        super(ChildCollectionField, self).__init__(**kwargs)

    def get_url(self, obj, view_name, request, format):
        parent_obj = obj.instance
        url = self.reverse(view_name, request=request, format=format)
        url = replace_query_param(url, self.parent_id_name, parent_obj.pk)

        return url


class GroupSerializer(HyperlinkedModelSerializer):
    feeds = ChildCollectionField(view_name='feed-list', read_only=True, parent_id_name='group_id')

    class Meta:
        model = Group
        fields = '__all__'


class FeedSerializer(HyperlinkedModelSerializer):
    articles = ChildCollectionField(view_name='article-list', read_only=True, parent_id_name='feed_id')

    class Meta:
        model = Feed
        fields = '__all__'


class ArticleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
