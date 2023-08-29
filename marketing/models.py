from django.db import models

class Subscriptions(models.Model):
    email = models.CharField(max_length=100)
