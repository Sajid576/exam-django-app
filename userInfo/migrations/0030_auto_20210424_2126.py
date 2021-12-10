# Generated by Django 3.1 on 2021-04-24 15:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userInfo', '0029_auto_20210424_0148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collegeinfo',
            name='grade',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)]),
        ),
        migrations.AlterField(
            model_name='schoolinfo',
            name='grade',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)]),
        ),
    ]