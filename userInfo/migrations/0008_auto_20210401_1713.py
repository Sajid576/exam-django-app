# Generated by Django 3.1 on 2021-04-01 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userInfo', '0007_auto_20210401_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useremail',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]