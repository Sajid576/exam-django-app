# Generated by Django 3.1 on 2021-04-28 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0018_auto_20210428_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='instruction',
            field=models.TextField(blank=True),
        ),
    ]
