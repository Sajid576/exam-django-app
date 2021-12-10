# Generated by Django 3.1 on 2021-02-13 12:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newsFeed', '0002_newsfeedcount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsfeedcount',
            name='news',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='counts', to='newsFeed.newsfeed'),
        ),
        migrations.AlterField(
            model_name='newsfeedimage',
            name='news',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='newsFeed.newsfeed'),
        ),
    ]
