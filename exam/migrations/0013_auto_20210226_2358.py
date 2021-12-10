# Generated by Django 3.1 on 2021-02-26 17:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('package', '0002_remove_package_ispaid'),
        ('exam', '0012_auto_20210221_1300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='examType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.examtype'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='package',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exams', to='package.package'),
        ),
    ]
