from django.db import models

class TokenKeys(models.Model):
    key = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'TokenKeys'

    def __str__(self):
        return self.key
