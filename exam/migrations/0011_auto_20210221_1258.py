# Generated by Django 3.1 on 2021-02-21 06:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0010_auto_20210220_1818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userexam',
            name='consumedTime',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
    ]
