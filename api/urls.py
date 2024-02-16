from . import views
from .views import MyTokenObtainPairView
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import MyTokenObtainPairView_Admin
from .views import MyTokenObtainPairView_Doctor

from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('api/', views.getRoutes),
    path('api/users', views.getUsers),

    path('api/create/', views.create_assessment),

    path('api/clinic/assessments', views.assessment),
    path('api/create/', views.create_assessment),
    path('api/create-user/', views.create_user),

    path('api/token/admin/', MyTokenObtainPairView_Admin.as_view(), name='token_obtain_pair_admin'),
    path('api/token/doctor/', MyTokenObtainPairView_Doctor.as_view(), name='token_obtain_pair_doctor'),

    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/resource', views.resourceHub),
    path('api/create-resource', views.create_ResourceItem),
    path('api/resource/<int:resource_id>/', views.delete_resource, name='delete_resource'),
    

    path('api/clinic/branches', views.clinicBranches),
    path('api/clinic/create-branch', views.create_clinicBranches),
    path('api/clinic/branch/delete/<int:branch_id>/', views.soft_delete_branch, name='delete_client'),
    
    path('api/clinic/admin-user', views.getAdminUsers),
    path('api/clinic/create-super-user', views.create_adminUser),

    path('api/clinic/create-doctor', views.create_doctor),
    path('api/doctors/<int:doctor_id>/', views.soft_delete_doctor, name='delete_doctor'),

    path('api/clinic/doctors', views.doctors),
    path('api/clinic/doctors/create-account', views.create_doctorUser),

    path('api/clinic/appointments', views.appointment),
    path('api/clinic/create-appointments', views.create_appointment),
    path('update-appointment/<int:appointment_id>/', views.update_appointment_time, name='update_appointment_time'),

    path('api/clinic/advance-appointments', views.advance_appointment),
    path('api/clinic/create-advance-appointments', views.create_advance_appointment),
    path('update-advance-appointment/<int:appointment_id>/', views.update_advance_appointment_time, name='update_appointment_time'),

    path('api/clinic/clients', views.clients),

    path('api/clinic/clients/notes/', views.client_notes),
    path('api/clinic/clients/create-notes', views.create_client_note),

    path('api/clinic/clients/update-status/<int:client_id>/', views.update_client_status, name='update_client_status'),
    path('api/clinic/clients/delete/<int:client_id>/', views.soft_delete_client, name='delete_client'),
    path('api/clinic/clients/create', views.create_client),

    path('api/change-password/', views.change_password),
    path('api/update-profile/', views.update_profile, name='update_profile'),

    path('verify/<str:uidb64>/<str:token>/', views.activate_account, name='activate_account'),

    path('api/check_email/', views.check_email, name='check_email'),
    path('api/check_username/', views.check_username, name='check_username'),

    path('check-time-slot-availability/<int:appointment_id>/', views.check_time_slot_availability, name='check_time_slot_availability'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
