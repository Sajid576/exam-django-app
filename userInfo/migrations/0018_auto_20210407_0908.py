# Generated by Django 3.1 on 2021-04-07 03:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userInfo', '0017_merge_20210406_2045'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schoolName', models.CharField(blank=True, max_length=254)),
                ('className', models.IntegerField(choices=[(1, 'class 1'), (2, 'class 2'), (3, 'class 3'), (4, 'class 4'), (5, 'class 5'), (6, 'class 6'), (7, 'class 7'), (8, 'class 8'), (9, 'class 9'), (10, 'class 10')], null=True)),
                ('boardName', models.IntegerField(choices=[(1, 'DHAKA'), (2, 'CHITTAGONG'), (3, 'CUMILLA'), (4, 'RAJSHAHI'), (5, 'DINAJPUR'), (6, 'BARISHAL'), (7, 'SYLHET'), (8, 'MYMENSINGH')], null=True)),
                ('field', models.CharField(blank=True, max_length=254)),
                ('startDate', models.DateField(null=True)),
                ('endDate', models.DateField(null=True)),
                ('currentStudent', models.BooleanField(default=False)),
                ('grade', models.FloatField(null=True)),
                ('activites', models.CharField(blank=True, max_length=254)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('completeness', models.IntegerField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='EducationInfo',
        ),
    ]
