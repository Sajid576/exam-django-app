# Generated by Django 3.1 on 2021-04-05 14:40

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userInfo', '0013_auto_20210405_2016'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='address',
            unique_together={('user', 'isPermanentAddress')},
        ),
    ]