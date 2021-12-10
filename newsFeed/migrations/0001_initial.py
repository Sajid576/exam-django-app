# Generated by Django 3.1 on 2021-02-12 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsFeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('details', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='NewsFeedImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='newsFeedImg')),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsFeed.newsfeed')),
            ],
        ),
    ]