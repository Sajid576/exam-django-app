# Generated by Django 3.1 on 2021-05-20 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_auto_20210520_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
