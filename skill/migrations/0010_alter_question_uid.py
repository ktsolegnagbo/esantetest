# Generated by Django 5.1.1 on 2024-09-24 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skill', '0009_question_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='uid',
            field=models.PositiveIntegerField(unique=True),
        ),
    ]
