# Generated by Django 5.1.1 on 2024-09-24 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skill', '0005_alter_question_question_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='already_done',
            field=models.BooleanField(default=False),
        ),
    ]
