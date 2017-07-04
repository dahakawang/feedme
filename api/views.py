from django.shortcuts import render
from rest_framework.viewsets import *
from api.serializers import *
from core_data.models import *

# Create your views here.


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all().order_by('title')
    serializer_class = GroupSerializer


class FeedViewSet(ModelViewSet):
    queryset = Feed.objects.all().order_by('title')
    serializer_class = FeedSerializer

    def get_queryset(self):
        query = self.queryset
        if 'group_id' in self.request.query_params:
            group_id = self.request.query_params['group_id']
            query = query.filter(group=group_id)
        return query


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all().order_by('title')
    serializer_class = ArticleSerializer

    def get_queryset(self):
        query = self.queryset
        if 'feed_id' in self.request.query_params:
            group_id = self.request.query_params['feed_id']
            query = query.filter(feed=group_id)
        return query
