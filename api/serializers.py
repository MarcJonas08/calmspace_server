from rest_framework.serializers import ModelSerializer
from .models import CustomUser
from .models import Assessments
from .models import ResourceHub
from .models import ClinicBranches, Doctor, Appointment, Clients, Note

class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class AssessmentsSerializer(ModelSerializer):
    class Meta:
        model = Assessments
        fields = '__all__'

class ResourceHubSerializer(ModelSerializer):
    class Meta:
        model = ResourceHub
        fields = '__all__'

class ClinicBranchesSerializer(ModelSerializer):
    class Meta:
        model = ClinicBranches
        fields = '__all__'

class AdminUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'branch', 'phone_number']

class DoctorSerializer(ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
        
class AppointmentSerializer(ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class ClientsSerializer(ModelSerializer):
    class Meta:
        model = Clients
        fields = '__all__'

class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'
