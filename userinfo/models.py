from django.db import models

# Create your models here.
class User(models.Model):
    uname = models.CharField(max_length=50,unique=True)
    upwd = models.CharField(max_length=200)
    uemail = models.EmailField(null=True)
    isdelete = models.BooleanField(default=False)

    def __str__(self):
        return self.uname


    class Meta:
        db_table = 'user'


