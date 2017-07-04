from core_data.models import *


def create(group):
    group.save()
    return group


def remove(id):
    group = Group.objects.get(id=id)
    group.delete()


def get(id):
    return Group.objects.get(id=id)


def get_all():
    return Group.objects.all()


def rename(id, new_title):
    group = Group.objects.get(id=id)
    group.title = new_title
    group.save()


def get_group_feed_mapping():
    mapping = []
    groups = Group.objects.all()
    for group in groups:
        feed_id_set = group.feed_set.values_list("id")
        feed_id_list = [t[0] for t in feed_id_set]
        mapping.append(GroupFeedIdMapping(group.id, feed_id_list))
