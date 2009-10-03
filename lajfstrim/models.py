from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    jid = models.EmailField(blank=True)
    site_title = models.CharField(max_length=255, blank=True)
    about_me = models.TextField(blank=True)

class Feed(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    etag = models.CharField(max_length=128, default=0)

    def __unicode__(self):
        return self.name

class Item(models.Model):
    user = models.ForeignKey(User)
    type = models.CharField(max_length=128)
    title = models.CharField(max_length=255, blank=True, null=True)
    link = models.CharField(max_length=255)
    date = models.DateTimeField(default=datetime.now())
    updated_date = models.DateTimeField(default=datetime.now())
    body = models.TextField()

    def __unicode__(self):
        return self.title
    
class Site(models.Model):
    SITE_CHOICES = (
        (u'blip', u'Blip.pl'),
        #(u'last', u'Last.fm'),
        (u'twitter', u'Twitter'),
        (u'identica', u'Identi.ca'),
    )
    user = models.ForeignKey(User)
    username = models.CharField(max_length=255)
    site = models.CharField(max_length=128, choices=SITE_CHOICES)

    def __unicode__(self):
        return self.site

class UserUserRelation(models.Model):
    user = models.ForeignKey(User)
    friend = models.ForeignKey(User, related_name='added')