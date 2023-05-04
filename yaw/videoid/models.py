from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Comment(models.Model):
    channel_id = models.CharField(max_length=30)
    video_id = models.CharField(max_length=30)
    comment_id = models.CharField(max_length=30)
    date = models.DateTimeField()
    author = models.CharField(max_length = 20)
    comment_text = models.TextField()

    def __str__(self):
        return self.video_id + ' ' + self.comment_id