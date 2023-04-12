from django.contrib.auth.models import AbstractUser
from django.db import models

from payapp.utils import convert_currency


class User(AbstractUser):
    CURRENCY_TYPE = (
        ('USD', 'USD'),
        ("GBP", 'GBP'),
        ("EURO", 'EURO'),
    )
    email = models.EmailField(unique=True, max_length=200)
    total_amount = models.FloatField(default=1000)
    sent_amount = models.FloatField(default=0)
    currency_type = models.CharField(max_length=20, choices=CURRENCY_TYPE, default='USD')

    REQUIRED_FIELDS = ['username', ]
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.username

    def get_name_info(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username

    def save(self, *args, **kwargs):
        """
        On save - user create -- convert (convert 1000 GBP to user selected currency)
        find code of currencies conversion inside : payapp.utils.convert_currency
        """
        self.total_amount = convert_currency("GBP", self.currency_type, self.total_amount)
        super(User, self).save(*args, **kwargs)

