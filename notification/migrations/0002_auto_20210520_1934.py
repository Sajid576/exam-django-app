# Generated by Django 3.1 on 2021-05-20 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='data',
            field=models.JSONField(null=True),
        ),
    ]
