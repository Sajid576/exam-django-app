# Generated by Django 3.1 on 2021-02-11 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('designcontest', '0003_auto_20210205_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestdata',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
