# Generated by Django 3.1 on 2021-02-11 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0006_merge_20210210_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='userexam',
            name='viewAble',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]