# Generated by Django 5.0 on 2024-01-06 05:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_remove_timeslot_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='date',
        ),
    ]
