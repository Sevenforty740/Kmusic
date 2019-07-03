from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True)
    USERNAME_FIELD = 'username'
    email = models.EmailField(_('email address'), blank=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    def __str__(self):
        return self.username

    objects = UserManager()

    class Meta:
        db_table = 'user'



