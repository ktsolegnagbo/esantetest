# Generated by Django 5.1.1 on 2024-09-24 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skill', '0007_remove_question_already_done_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='default',
            field=models.TextField(default='-'),
        ),
    ]
