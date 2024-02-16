# Generated by Django 5.0 on 2024-01-14 08:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_remove_note_client_delete_clients_delete_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('age', models.CharField(max_length=3)),
                ('birthday', models.DateField()),
                ('contact_number', models.CharField(max_length=11)),
                ('emergency_contact_number', models.CharField(max_length=11)),
                ('email', models.EmailField(max_length=254)),
                ('appointment_date', models.DateField()),
                ('appointment_time', models.CharField(max_length=50)),
                ('medical_history', models.CharField(max_length=1000)),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed')], default='active', max_length=10)),
                ('appointment_type', models.CharField(choices=[('online', 'Online'), ('face_to_face', 'Face to Face')], default='face_to_face', max_length=20)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.clinicbranches')),
                ('doctor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.doctor')),
                ('userID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.clients')),
            ],
        ),
    ]
