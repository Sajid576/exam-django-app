# Generated by Django 3.1 on 2021-02-14 06:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newsFeed', '0003_auto_20210213_1841'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NewsFeedCount',
        ),
    ]