# Generated by Django 5.0 on 2024-01-14 08:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_rename_client_id_clients_userid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='client',
        ),
        migrations.DeleteModel(
            name='Clients',
        ),
        migrations.DeleteModel(
            name='Note',
        ),
    ]
