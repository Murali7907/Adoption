from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.profile_view, name='dashboard'),
    path('social/<str:provider>/', views.social_auth_view, name='social_auth'),
    path('logout/', views.logout_view, name='logout'),
    path('api/send-otp/', views.api_send_otp, name='api_send_otp'),
    path('api/verify-otp/', views.api_verify_otp, name='api_verify_otp'),
    path('api/reset-password/', views.api_reset_password, name='api_reset_password'),
    path('api/admin/verify-profile/', views.api_admin_verify_user, name='api_admin_verify_user'),
    path('api/admin/create-shelter/', views.api_admin_create_shelter, name='api_admin_create_shelter'),
    path('api/shelter/create-delivery/', views.api_shelter_create_delivery, name='api_shelter_create_delivery'),
    path('api/shelter/create-pet/', views.api_shelter_create_pet, name='api_shelter_create_pet'),
    path('api/update-profile/', views.api_update_profile, name='api_update_profile'),
    path('api/notify-adoption/', views.api_notify_adoption, name='api_notify_adoption'),
    path('api/purge-adoption-data/', views.api_purge_adoption_data, name='api_purge_adoption_data'),
    path('api/admin/toggle-active/', views.api_admin_toggle_user_active, name='api_admin_toggle_user_active'),
    path('api/admin/delete-user/', views.api_admin_delete_user, name='api_admin_delete_user'),
    path('api/admin/save-settings/', views.api_admin_save_settings, name='api_admin_save_settings'),
    path('api/admin/save-permissions/', views.api_admin_save_permissions, name='api_admin_save_permissions'),
]

