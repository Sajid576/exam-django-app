# Generated by Django 3.1 on 2021-02-14 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsFeed', '0004_delete_newsfeedcount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsfeedimage',
            name='image',
            field=models.IntegerField(),
        ),
    ]