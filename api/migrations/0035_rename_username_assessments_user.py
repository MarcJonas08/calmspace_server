# Generated by Django 5.0 on 2024-01-14 05:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_clients_client_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assessments',
            old_name='username',
            new_name='user',
        ),
    ]
