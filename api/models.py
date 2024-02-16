from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from django.db import models


class ClinicBranches(models.Model):
    branch_name = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255, null=True, blank=True)
    barangay = models.CharField(max_length=255, null=True, blank=True)
    city_town = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.branch_name
    
class Doctor(models.Model):
    branch_name = models.ForeignKey(ClinicBranches, on_delete=models.CASCADE)
    doctor_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=11)
    email = models.EmailField()
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.doctor_name
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    branch = models.ForeignKey(ClinicBranches, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    is_doctor = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

class Assessments(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    AnxietyScore = models.CharField(max_length=600, default='', blank=True, null=True)
    

class ResourceHub(models.Model):
    image = models.ImageField(upload_to='images/')
    description = models.CharField(max_length=255)
    title = models.CharField(max_length=100)
    link = models.URLField()

    RESOURCE_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('news', 'News'),
    ]

    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)

    def delete(self, *args, **kwargs):
        # Get the image path before deleting the object
        image_path = self.image.path

        # Delete the object
        super(ResourceHub, self).delete(*args, **kwargs)

        # Delete the image file if it exists
        if os.path.exists(image_path):
            os.remove(image_path)

    def __str__(self):
        return self.title


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    branch = models.ForeignKey(ClinicBranches, on_delete=models.CASCADE)
    time_8am_9am = models.BooleanField(default=True)
    time_9am_10am = models.BooleanField(default=True)
    time_10am_11am = models.BooleanField(default=True)
    time_11am_12pm = models.BooleanField(default=True)
    time_1pm_2pm = models.BooleanField(default=True)
    time_2pm_3pm = models.BooleanField(default=True)
    time_3pm_4pm = models.BooleanField(default=True)
    time_4pm_5pm = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.doctor} - {self.branch}"

class AdvanceAppointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    branch = models.ForeignKey(ClinicBranches, on_delete=models.CASCADE)
    time_8am_9am = models.BooleanField(default=True)
    time_9am_10am = models.BooleanField(default=True)
    time_10am_11am = models.BooleanField(default=True)
    time_11am_12pm = models.BooleanField(default=True)
    time_1pm_2pm = models.BooleanField(default=True)
    time_2pm_3pm = models.BooleanField(default=True)
    time_3pm_4pm = models.BooleanField(default=True)
    time_4pm_5pm = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.doctor} - {self.branch}"
    
class Clients(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.CharField(max_length=3)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    birthday = models.DateField() 
    contact_number = models.CharField(max_length=11)
    emergency_contact_number = models.CharField(max_length=11)
    email = models.EmailField()

    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.CharField(max_length=50)

    medical_history = models.CharField(max_length=1000, null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    branch = models.ForeignKey(ClinicBranches, on_delete=models.CASCADE)

    userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    # Address Fields
    street_address = models.CharField(max_length=255, null=True, blank=True)
    barangay = models.CharField(max_length=255, null=True, blank=True)
    city_town = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Note(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f'{self.client.first_name} {self.client.last_name}'