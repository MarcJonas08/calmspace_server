# Generated by Django 5.0 on 2024-01-06 05:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_appointment_time_3pm_4pm'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeslot',
            name='date',
        ),
    ]
