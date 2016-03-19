from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Thread(models.Model):
    date_time = models.DateTimeField()
    topic = models.TextField()
    author = models.CharField(max_length=100)
    hit = models.IntegerField()
    emotion = models.CharField(max_length=10)
    url = models.URLField()

    def __str__(self):
        return self.topic

class Post(models.Model):
    date_time = models.DateTimeField()
    author = models.CharField(max_length=100)
    topic = models.TextField()
    content = models.TextField()
    emotion = models.CharField(max_length=10)
    url = models.URLField()
    thread = models.ForeignKey(Thread)
    adj = ArrayField(models.CharField(max_length=20))
    noun = ArrayField(models.CharField(max_length=20))
    positive_words = ArrayField(models.CharField(max_length=20))
    negative_words = ArrayField(models.CharField(max_length=20))
    neutral_words = ArrayField(models.CharField(max_length=20))

    def __str__(self):
        return self.topic
