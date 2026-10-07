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
    path('api/delivery/update-status/', views.api_delivery_update_status, name='api_delivery_update_status'),
    path('api/delivery/upload-proof/', views.api_delivery_upload_proof, name='api_delivery_upload_proof'),
    path('api/shelter/assign-delivery/', views.api_shelter_assign_delivery, name='api_shelter_assign_delivery'),
    path('api/shelter/update-adoption-status/', views.api_update_adoption_status, name='api_update_adoption_status'),
    path('api/get-conversations/', views.api_get_conversations, name='api_get_conversations'),
    path('api/get-messages/', views.api_get_messages, name='api_get_messages'),
    path('api/send-message/', views.api_send_message, name='api_send_message'),
    # Phase 7 & 8: Shelter document upload & storage endpoints
    path('api/shelter/upload-document/', views.api_shelter_upload_document, name='api_shelter_upload_document'),
    path('api/shelter/list-documents/', views.api_shelter_list_documents, name='api_shelter_list_documents'),
    path('api/shelter/delete-document/', views.api_shelter_delete_document, name='api_shelter_delete_document'),
    path('api/shelter/document/<int:doc_id>/download/', views.api_shelter_download_document, name='api_shelter_download_document'),
    # Phase 18: Shelter Dossier update endpoint
    path('api/shelter/update-profile/', views.api_shelter_update_profile, name='api_shelter_update_profile'),
    # Phase 9: Admin document verification endpoints
    path('api/admin/shelter-documents/', views.api_admin_list_shelter_documents, name='api_admin_list_shelter_documents'),
    path('api/admin/verify-document/', views.api_admin_verify_document, name='api_admin_verify_document'),
    path('api/admin/verify-all-shelter-documents/', views.api_admin_verify_all_shelter_documents, name='api_admin_verify_all_shelter_documents'),
    path('api/adoption/apply/', views.api_apply_adoption, name='api_apply_adoption'),
    path('api/shelter/update-pet-status/', views.api_update_pet_status, name='api_update_pet_status'),
    path('api/delivery/toggle-availability/', views.api_delivery_toggle_availability, name='api_delivery_toggle_availability'),
    path('api/delivery/available-partners/', views.api_get_available_delivery_partners, name='api_get_available_delivery_partners'),
    path('api/shelter/verification-status/', views.api_shelter_verification_status, name='api_shelter_verification_status'),
    path('api/appointment/reschedule/', views.api_reschedule_appointment, name='api_reschedule_appointment'),
    path('api/appointment/confirm-reschedule/', views.api_confirm_rescheduled_appointment, name='api_confirm_rescheduled_appointment'),
    path('api/favorite/toggle/', views.api_toggle_favorite, name='api_toggle_favorite'),
]


