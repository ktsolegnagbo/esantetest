# Generated by Django 5.1.1 on 2024-10-01 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skill', '0013_rename_tme_left_appuser_time_left'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appuser',
            name='started',
            field=models.BooleanField(default=False),
        ),
    ]
