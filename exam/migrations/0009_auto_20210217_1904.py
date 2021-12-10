# Generated by Django 3.1 on 2021-02-17 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0008_auto_20210212_0520'),
    ]

    operations = [
        migrations.AddField(
            model_name='userexam',
            name='consumedTime',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='userexam',
            name='examDate',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='userexam',
            name='obtainedMarks',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='userexam',
            name='retakeAble',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='userexam',
            name='totalCorrectedQuestions',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='userexam',
            name='viewAble',
            field=models.BooleanField(null=True),
        ),
    ]