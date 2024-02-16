from django.contrib import admin
from .models import CustomUser
from .models import Assessments
from .models import ResourceHub
from .models import ClinicBranches
from .models import Doctor, Appointment, Clients, Note, AdvanceAppointment


# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Assessments)
admin.site.register(ResourceHub)
admin.site.register(ClinicBranches)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Clients)
admin.site.register(Note)
admin.site.register(AdvanceAppointment)