# Generated by Django 3.1 on 2021-04-14 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userInfo', '0024_auto_20210412_0029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, max_length=512, null=True, upload_to='profilePics'),
        ),
    ]