from django.conf.urls import url, include
from rest_framework import routers
from api.views import *

router = routers.DefaultRouter()
router.register(r'groups', GroupViewSet)
router.register(r'feeds', FeedViewSet)
router.register(r'articles', ArticleViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]