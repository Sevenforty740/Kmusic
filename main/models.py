from django.db import models
from userinfo.models import User

# Create your models here.
class Songlist(models.Model):
    listname = models.CharField(max_length=200)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    isdelete = models.BooleanField(default=False)

    def __str__(self):
        return self.listname

    class Meta:
        db_table = 'songlist'


class Song(models.Model):
    songid = models.CharField(max_length=200)
    source = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    duration = models.CharField(max_length=50)
    songlist = models.ForeignKey(Songlist,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'song'