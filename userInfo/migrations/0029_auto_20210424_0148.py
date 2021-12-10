# Generated by Django 3.1 on 2021-04-23 19:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userInfo', '0028_auto_20210423_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, max_length=255, null=True, upload_to='CollegePics')),
                ('name', models.CharField(max_length=255)),
                ('establishDate', models.DateField(null=True)),
                ('scienceDept', models.BooleanField(default=True)),
                ('commerceDept', models.BooleanField(default=True)),
                ('artsDept', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterField(
            model_name='collegeinfo',
            name='boardName',
            field=models.IntegerField(choices=[(1, 'DHAKA'), (2, 'CHITTAGONG'), (3, 'CUMILLA'), (4, 'RAJSHAHI'), (5, 'DINAJPUR'), (6, 'BARISHAL'), (7, 'SYLHET'), (8, 'MYMENSINGH')], null=True),
        ),
        migrations.AlterField(
            model_name='collegeinfo',
            name='className',
            field=models.IntegerField(choices=[(1, 'class 11'), (2, 'class 12')], null=True),
        ),
        migrations.AlterField(
            model_name='collegeinfo',
            name='field',
            field=models.IntegerField(choices=[(1, 'SCIENCE'), (2, 'COMMERCE'), (3, 'ARTS')], null=True),
        ),
        migrations.AlterField(
            model_name='schoolinfo',
            name='boardName',
            field=models.IntegerField(choices=[(1, 'DHAKA'), (2, 'CHITTAGONG'), (3, 'CUMILLA'), (4, 'RAJSHAHI'), (5, 'DINAJPUR'), (6, 'BARISHAL'), (7, 'SYLHET'), (8, 'MYMENSINGH')], null=True),
        ),
        migrations.AlterField(
            model_name='schoolinfo',
            name='className',
            field=models.IntegerField(choices=[(1, 'class 1'), (2, 'class 2'), (3, 'class 3'), (4, 'class 4'), (5, 'class 5'), (6, 'class 6'), (7, 'class 7'), (8, 'class 8'), (9, 'class 9'), (10, 'class 10')], null=True),
        ),
        migrations.AlterField(
            model_name='schoolinfo',
            name='field',
            field=models.IntegerField(choices=[(1, 'SCIENCE'), (2, 'COMMERCE'), (3, 'ARTS')], null=True),
        ),
        migrations.AlterField(
            model_name='universityinfo',
            name='degreeName',
            field=models.IntegerField(choices=[(1, 'PRIMARY'), (2, 'SSC'), (3, 'HSC'), (4, 'BACHELOR'), (5, 'MASTERS'), (6, 'OTHERS')], null=True),
        ),
        migrations.AlterField(
            model_name='collegeinfo',
            name='collegeName',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userInfo.college'),
        ),
    ]
