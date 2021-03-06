# Generated by Django 3.1 on 2021-05-27 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userInfo', '0034_auto_20210512_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='college',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userInfo.countries'),
        ),
        migrations.AddField(
            model_name='school',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userInfo.countries'),
        ),
        migrations.AddField(
            model_name='university',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userInfo.countries'),
        ),
    ]
