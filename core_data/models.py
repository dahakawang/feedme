from django.db import models
from django.core import serializers

# Create your models here.


class Group(models.Model):
    title = models.TextField()

    def __str__(self):
        return serializers.serialize("json", [self])


class Favicon(models.Model):
    data = models.TextField()

    def __str__(self):
        return serializers.serialize("json", [self])


class Feed(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    favicon = models.ForeignKey(Favicon, on_delete=models.SET_NULL, null=True)
    title = models.TextField()
    url = models.TextField()
    site_url = models.TextField()
    last_updated_time = models.DateTimeField()

    def __str__(self):
        return serializers.serialize("json", [self])


class Article(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    title = models.TextField()
    author = models.TextField()
    html = models.TextField()
    url = models.TextField()
    is_read = models.BooleanField()
    is_stared = models.BooleanField()
    created_time = models.DateTimeField()

    def __str__(self):
        return serializers.serialize("json", [self])
