# Generated by Django 5.0 on 2024-01-10 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_note'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='branch',
        ),
    ]
