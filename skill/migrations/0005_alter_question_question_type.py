# Generated by Django 5.1.1 on 2024-09-24 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skill', '0004_question_default_question_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('text', 'Texte'), ('python', 'Code Python'), ('nodejs', 'Code NodeJs'), ('sql', 'Code Sql'), ('qcm_m', 'Choix Multiple'), ('qcm_u', 'Choix Unique')], default='text', max_length=10),
        ),
    ]
