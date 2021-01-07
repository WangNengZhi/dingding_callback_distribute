from django.db import models


class DingTag(models.Model):
    url = models.ForeignKey('Url', models.DO_NOTHING)
    tag = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)
    modify_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ding_tag'


class Url(models.Model):
    url = models.CharField(max_length=200, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)
    modify_date = models.DateTimeField(blank=True, null=True)
    path = models.CharField(max_length=255)
    db_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'url'
