# Generated by Django 3.1 on 2021-02-14 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsFeed', '0005_auto_20210214_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsfeedimage',
            name='image',
            field=models.ImageField(upload_to='quesImg'),
        ),
    ]
