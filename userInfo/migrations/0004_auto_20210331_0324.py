# Generated by Django 3.1 on 2021-03-30 21:24

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userInfo', '0003_auto_20210331_0320'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='useremail',
            unique_together={('user', 'email')},
        ),
        migrations.AlterUniqueTogether(
            name='usermobile',
            unique_together={('user', 'mobile')},
        ),
    ]