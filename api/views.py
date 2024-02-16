from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import CustomUser
from .serializers import CustomUserSerializer
from .serializers import AssessmentsSerializer
from .serializers import ResourceHubSerializer
from .serializers import ClinicBranchesSerializer
from .serializers import AdminUserSerializer, DoctorSerializer, AppointmentSerializer, ClientsSerializer, NoteSerializer, UserSerializer
from .models import Assessments
from .models import ResourceHub
from .models import ClinicBranches
from .models import Doctor, Appointment, Clients, Note, AdvanceAppointment

from rest_framework import viewsets



from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse
from rest_framework.decorators import api_view
from .tokens import account_activation_token
from django.utils.encoding import force_str
from django.shortcuts import redirect



# Create your views here.

@api_view(['GET'])
def getRoutes(request):
    users = CustomUser.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUsers(request):
    users = CustomUser.objects.all()
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_assessment(request):
    data = request.data
    user_id = data.get('user_id')
    
    try:
        user_instance = CustomUser.objects.get(id=user_id)
        assessment, created = Assessments.objects.get_or_create(
            user=user_instance,
            defaults={'AnxietyScore': data.get('AnxietyScore')}
        )

        if not created:
            # Update existing assessment
            assessment.AnxietyScore = data.get('AnxietyScore')
            assessment.save()

        serializer = AssessmentsSerializer(assessment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except CustomUser.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assessment(request):

    assessment = Assessments.objects.all()
    serializer = AssessmentsSerializer(assessment, many=True)
    return Response(serializer.data)
    
    

@api_view(['POST'])
def create_user(request):
    data = request.data 

    user = CustomUser.objects.create_user(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        username=data.get('username'),
        email=data.get('email'),
        phone_number=data.get('phone_number'),
        gender=data.get('gender'),
        password=data.get('password'),
        is_active=False,  # User is inactive until email is verified
    )

    # Generate verification token
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Build verification URL
    current_site = get_current_site(request)
    verification_link = f"http://{current_site.domain}/verify/{uid}/{token}/"

    # Compose email
    subject = 'Activate Your Account'
    message = render_to_string('activation_email.html', {
        'user': user,
        'verification_link': verification_link,
    })
    send_mail(subject, message, 'from@example.com', [user.email], html_message=message)

    serializer = CustomUserSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('https://calm-space.online')
    else:
        return HttpResponse('Activation link is invalid!')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = CustomUser.EMAIL_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = CustomUser.objects.filter(email=attrs[self.username_field]).first()

        if not user:
            raise serializers.ValidationError('The user is not valid.')

        if not user.check_password(attrs['password']):
            raise serializers.ValidationError('Incorrect credentials.')

        self.user = user
        data = super().validate(attrs)

        # Add custom claims if needed
        token = self.get_token(self.user)
        # Add custom claims to the token
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['phone_number'] = user.phone_number
        token['email'] = user.email

        data['refresh'] = str(token)
        data['access'] = str(token.access_token)

        return data

    def get_token(self, user):
        return RefreshToken.for_user(user)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def resourceHub(request):

    resourceHub_news = ResourceHub.objects.filter(resource_type='news')
    resourceHub_article = ResourceHub.objects.filter(resource_type='article')
    resourceHub_video = ResourceHub.objects.filter(resource_type='video')

    serialized_news = ResourceHubSerializer(resourceHub_news, many=True).data
    serialized_article = ResourceHubSerializer(resourceHub_article, many=True).data
    serialized_video = ResourceHubSerializer(resourceHub_video, many=True).data

    response_data = {
        'news': serialized_news,
        'article': serialized_article,
        'video': serialized_video,
    }

    return Response(response_data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_resource(request, resource_id):
    try:
        resource = ResourceHub.objects.get(pk=resource_id)
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ResourceHub.DoesNotExist:
        return Response({'error': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)
    

from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from .models import CustomUser

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser

class MyTokenObtainPairSerializer_Admin(TokenObtainPairSerializer):
    username_field = CustomUser.EMAIL_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = CustomUser.objects.filter(email=attrs[self.username_field]).first()

        if not user:
            raise serializers.ValidationError('The user is not valid.')

        if not user.check_password(attrs['password']):
            raise serializers.ValidationError('Incorrect credentials.')

        if not user.is_active or not user.is_superuser:
            raise serializers.ValidationError('Only superusers are allowed to log in.')

        if user.is_doctor:
            raise serializers.ValidationError('Only users with is_doctor=False are allowed to log in.')

        self.user = user
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data

    def get_token(self, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['gender'] = user.gender
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['phone_number'] = user.phone_number
        token['email'] = user.email

        if user.branch:
            token['branch'] = {
                'branch_name': user.branch.branch_name,
                'id': user.branch.id,
                # Add other fields as needed
            }
        else:
            token['full_name'] = None
        # ...

        return token

class MyTokenObtainPairView_Admin(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer_Admin



class MyTokenObtainPairSerializer_Doctor(TokenObtainPairSerializer):
    username_field = CustomUser.EMAIL_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = CustomUser.objects.filter(email=attrs[self.username_field]).first()

        if not user:
            raise serializers.ValidationError('The user is not valid.')

        if not user.check_password(attrs['password']):
            raise serializers.ValidationError('Incorrect credentials.')

        if not user.is_active or not user.is_superuser:
            raise serializers.ValidationError('Only superusers are allowed to log in.')

        if not user.is_doctor:
            raise serializers.ValidationError('Only users with is_doctor=True are allowed to log in.')

        self.user = user
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data

    def get_token(self, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['phone_number'] = user.phone_number
        token['email'] = user.email

        if user.branch:
            token['branch'] = {
                'branch_name': user.branch.branch_name,
                'id': user.branch.id,
                # Add other fields as needed
            }
        else:
            token['full_name'] = None

        if user.full_name:
            token['full_name'] = {
                'doctor_name': user.full_name.doctor_name,
                'contact_number': user.full_name.contact_number,
                'email': user.full_name.email,
                'id': user.full_name.id,
                # Add other fields as needed
            }
        else:
            token['full_name'] = None
        # ...

        return token

class MyTokenObtainPairView_Doctor(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer_Doctor

@api_view(['GET'])
def clinicBranches(request):
    branches = ClinicBranches.objects.all()
    serializer = ClinicBranchesSerializer(branches, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_clinicBranches(request):
    data = request.data

    branch = ClinicBranches.objects.create(
        branch_name = data.get('branch_name'),
        street_address =  data.get('street_address'),
        barangay =  data.get('barangay'),
        city_town =  data.get('city_town'),
        province =  data.get('province'),
        postal_code =  data.get('postal_code'),
        country =  data.get('country'),
        is_deleted = False,
    )

    serializer = ClinicBranchesSerializer(branch)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_adminUser(request):
    data = request.data 

    branchId = data.get('branch')
    branch_instance = ClinicBranches.objects.get(id=branchId)

    

    user = CustomUser.objects.create_superuser(
        username = data.get('username'),
        email = data.get('email'),
        phone_number = data.get('phone_number'),
        password = data.get('password'),
        branch = branch_instance,
        is_active = False,
    )

    # Generate verification token
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Build verification URL
    current_site = get_current_site(request)
    verification_link = f"http://{current_site.domain}/verify/{uid}/{token}/"

    # Compose email
    subject = 'Activate Your Account'
    message = render_to_string('activation_email.html', {
        'user': user,
        'verification_link': verification_link,
    })
    send_mail(subject, message, 'from@example.com', [user.email], html_message=message)

    serializer = CustomUserSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_doctorUser(request):
    data = request.data 

    # Check if 'full_name' exists in the data
    if 'full_name' in data:
        doctorId = data['full_name']
        fullName = Doctor.objects.get(id=doctorId)
    else:
        fullName = None

    branchId = data.get('branch')
    branch_instance = ClinicBranches.objects.get(id=branchId)
    
    user = CustomUser.objects.create_superuser(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        full_name=fullName,
        username=data.get('username'),
        email=fullName.email,
        phone_number=fullName.contact_number,
        gender=data.get('gender'),
        password=data.get('password'),
        is_doctor=data.get('is_doctor'),
        branch = branch_instance,
        is_active = False,
    )

    # Generate verification token
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Build verification URL
    current_site = get_current_site(request)
    verification_link = f"http://{current_site.domain}/verify/{uid}/{token}/"

    # Compose email
    subject = 'Activate Your Account'
    message = render_to_string('activation_email.html', {
        'user': user,
        'verification_link': verification_link,
    })
    send_mail(subject, message, 'from@example.com', [user.email], html_message=message)

    serializer = CustomUserSerializer(user)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    doctor.delete()
    return Response({'message': 'Doctor deleted successfully.'}, status=200)

@api_view(['GET'])
def getAdminUsers(request):
    # Filter users to get only superusers
    superusers = CustomUser.objects.filter(is_superuser=True)
    
    serializer = AdminUserSerializer(superusers, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ResourceItem(request):
    data = request.data

    # Check if the request contains the image data
    if 'image' in request.FILES:
        image_file = request.FILES['image']
        # Save the image to the filesystem
        image_obj = ResourceHub.objects.create(
            image=image_file,
            description=data.get('description'),
            title=data.get('title'),
            link=data.get('link'),
            resource_type=data.get('resource_type')
            )
        # Store the reference to the uploaded image in the data dictionary
        data['image'] = image_obj.id
        serializer = ResourceHubSerializer(image_obj, many=False)
        return Response(serializer.data, status=201)
    else:
        # Handle the case when no image is provided
        return Response({'error': 'No image found in the request'}, status=400)


from rest_framework import status

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_resource_item(request, pk):
    try:
        resource = ResourceHub.objects.get(pk=pk)
    except ResourceHub.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    resource.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_doctor(request):

    data = request.data

    branch_name = data.get('branch_name')

    Clinic_branch_instance = ClinicBranches.objects.get(id=branch_name)

    doctor = Doctor.objects.create(
        branch_name = Clinic_branch_instance,
        doctor_name = data.get('doctor_name'),
        contact_number = data.get('contact_number'),
        email = data.get('email'),
    )

    serializer = DoctorSerializer(doctor)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctors(request):

    branches = Doctor.objects.all()

    serializer = DoctorSerializer(branches, many=True)
    return Response(serializer.data)

from datetime import date

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_appointment(request):

    data = request.data

    branchId = data.get('branch_name')
    print('BRANCH ID: ', branchId)
    Clinic_branch_instance = ClinicBranches.objects.get(id=branchId)

    doctorId = data.get('doctor_name')
    Doctor_instance = Doctor.objects.get(id=doctorId)

    appointment = Appointment.objects.create(
        branch = Clinic_branch_instance,
        doctor = Doctor_instance,
        time_8am_9am = False,
        time_9am_10am = False,
        time_10am_11am = False,
        time_11am_12pm = False,
        time_1pm_2pm = False,
        time_2pm_3pm = False,
        time_3pm_4pm = False,
        time_4pm_5pm = False
    )

    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment(request):

    appointment = Appointment.objects.all()
    
    serializer = AppointmentSerializer(appointment, many=True)
    return Response(serializer.data)

from django.shortcuts import get_object_or_404

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_appointment_time(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    # Assuming the request data contains the updated field and value (e.g., {"time_8am_9am": false})
    updated_data = request.data
    
    # Convert string values to booleans
    for field, value in updated_data.items():
        if hasattr(appointment, field):
            # Convert the value to a boolean
            boolean_value = value.lower() == 'true' if isinstance(value, str) else bool(value)
            setattr(appointment, field, boolean_value)

    # Save the updated appointment
    appointment.save()

    return Response({'message': 'Appointment time updated successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_notes(request):

    note = Note.objects.all()
    
    serializer = NoteSerializer(note, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_client_note(request):

    data = request.data

    clientId = data.get('clientId')
    client_instance = Clients.objects.get(id=clientId)

    note = Note.objects.create(
        client = client_instance,
        content = data.get('content'),
    )

    serializer = NoteSerializer(note)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clients(request):

    client = Clients.objects.all()
    
    serializer = ClientsSerializer(client, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_client(request):

    data = request.data

    branchId = data.get('branch')
    branch_instance = ClinicBranches.objects.get(id=branchId)

    doctorId = data.get('doctor')
    doctor_instance = Doctor.objects.get(id=doctorId)

    userId = data.get('userID')
    
    if userId:
        user_instance = CustomUser.objects.get(id=userId)
    else:
        user_instance = None
    
    client = Clients.objects.create(
        first_name = data.get('first_name'),
        last_name = data.get('last_name'),
        age = data.get('age'),
        gender = data.get('gender'),
        birthday = data.get('birthday'),
        contact_number = data.get('contact_number'),
        emergency_contact_number = data.get('emergency_contact_number'),
        email = data.get('email'),
        doctor_id = doctor_instance,
        appointment_date = data.get('appointment_date'),
        appointment_time = data.get('appointment_time'),
        medical_history = data.get('medical_history'),
        status = data.get('status'),
        branch = branch_instance,
        userID = user_instance,
        street_address = data.get('street_address'),
        barangay = data.get('barangay'),
        city_town = data.get('city_town'),
        province = data.get('province'),
        postal_code = data.get('postal_code'),
        country = data.get('country'),
    )

    serializer = ClientsSerializer(client)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_client_status(request, client_id):
    try:
        client = Clients.objects.get(pk=client_id)
    except Clients.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

    # Update the client's status
    client.status = request.data.get('status')
    client.save()

    # You can customize the response data as needed
    response_data = {
        'id': client.id,
        'status': client.status,
        # Include other fields as needed
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_client(request, client_id):
    try:
        client = Clients.objects.get(id=client_id)
    except Clients.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

    client.delete()
    return Response({'message': 'Client deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_advance_appointment(request):

    data = request.data

    branchId = data.get('branch_name')
    print('BRANCH ID: ', branchId)
    Clinic_branch_instance = ClinicBranches.objects.get(id=branchId)

    doctorId = data.get('doctor_name')
    Doctor_instance = Doctor.objects.get(id=doctorId)

    appointment = AdvanceAppointment.objects.create(
        branch = Clinic_branch_instance,
        doctor = Doctor_instance,
        time_8am_9am = False,
        time_9am_10am = False,
        time_10am_11am = False,
        time_11am_12pm = False,
        time_1pm_2pm = False,
        time_2pm_3pm = False,
        time_3pm_4pm = False,
        time_4pm_5pm = False
    )

    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def advance_appointment(request):

    appointment = AdvanceAppointment.objects.all()
    
    serializer = AppointmentSerializer(appointment, many=True)
    return Response(serializer.data)

from django.shortcuts import get_object_or_404

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_advance_appointment_time(request, appointment_id):
    appointment = get_object_or_404(AdvanceAppointment, pk=appointment_id)

    # Assuming the request data contains the updated field and value (e.g., {"time_8am_9am": false})
    updated_data = request.data
    
    # Convert string values to booleans
    for field, value in updated_data.items():
        if hasattr(appointment, field):
            # Convert the value to a boolean
            boolean_value = value.lower() == 'true' if isinstance(value, str) else bool(value)
            setattr(appointment, field, boolean_value)

    # Save the updated appointment
    appointment.save()

    return Response({'message': 'Appointment time updated successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    data = request.data

    # Log received data for troubleshooting
    print(f"Received data: {data}")
    print(f"user: {user}")

    # Check if the old password is correct
    form = PasswordChangeForm(user, data)
    if form.is_valid():
        # Change the password
        new_password = data.get('new_password2')  # Use new_password1
        user.set_password(new_password)
        user.save()

        # Update the session to avoid the user being logged out
        update_session_auth_hash(request, user)
        print(f"Form errors: {form}")

        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
    else:
        # Print form errors for troubleshooting
        print(f"Form errors: {form.errors}")

        # Provide detailed error messages
        errors = {field: form.errors[field][0] for field in form.errors}
        return Response({'message': 'Bad Request', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user

    # Extract data from the request's JSON payload
    data = request.data
    user_data = data.get('user', {})
    profile_info = data.get('profileInfo', {})

    try:
        # Update the user profile information
        user.first_name = profile_info.get('firstname', user.first_name)
        user.last_name = profile_info.get('lastname', user.last_name)
        user.username = profile_info.get('username', user.username)
        user.phone_number = profile_info.get('contact', user.phone_number)
        user.email = profile_info.get('email', user.email)
        
        # Save the changes
        user.save()

        return Response({'message': 'Profile updated successfully'})
    except Exception as e:
        return Response({'message': str(e)}, status=400)

@api_view(['GET'])
def check_email(request):
    if request.method == 'GET':
        email = request.GET.get('email', None)
        data = {
            'is_taken': CustomUser.objects.filter(email=email).exists()
        }
        return Response(data)
    else:
        return Response({'error': 'Method not allowed'}, status=405)

@api_view(['GET'])
def check_username(request):
    if request.method == 'GET':
        username = request.GET.get('username', None)
        data = {
            'is_taken': CustomUser.objects.filter(username=username).exists()
        }
        return Response(data)
    else:
        return Response({'error': 'Method not allowed'}, status=405)
    
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def soft_delete_doctor(request, doctor_id):

    # Retrieve the doctor instance based on the primary key (pk)
    doctor = get_object_or_404(Doctor, pk=doctor_id)

    # Update the is_deleted field to True
    doctor.is_deleted = True
    doctor.save()

    # Return a JSON response indicating success
    return Response({'message': 'Doctor soft deleted successfully'}, status=200)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def soft_delete_client(request, client_id):

    # Retrieve the doctor instance based on the primary key (pk)
    client = get_object_or_404(Clients, pk=client_id)

    # Update the is_deleted field to True
    client.is_deleted = True
    client.save()

    # Return a JSON response indicating success
    return Response({'message': 'Doctor soft deleted successfully'}, status=200)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def soft_delete_branch(request, branch_id):

    # Retrieve the doctor instance based on the primary key (pk)
    branch = get_object_or_404(ClinicBranches, pk=branch_id)

    # Update the is_deleted field to True
    branch.is_deleted = True
    branch.save()

    # Return a JSON response indicating success
    return Response({'message': 'Clinic Branch soft deleted successfully'}, status=200)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

@api_view(['POST'])
def check_time_slot_availability(request, appointment_id):
    if request.method == 'POST':
        appointment_type = request.data.get('appointment_type')
        appointment_time = request.data.get('appointment_time')

        if appointment_type == 'appointment':
            appointment = get_object_or_404(Appointment, id=appointment_id)
            time_field_value = getattr(appointment, appointment_time)
        else:
            advance_appointment = get_object_or_404(AdvanceAppointment, id=appointment_id)
            time_field_value = getattr(advance_appointment, appointment_time)

        return Response({'available': time_field_value})