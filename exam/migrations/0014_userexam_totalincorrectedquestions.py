# Generated by Django 3.1 on 2021-03-05 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0013_auto_20210226_2358'),
    ]

    operations = [
        migrations.AddField(
            model_name='userexam',
            name='totalIncorrectedQuestions',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
