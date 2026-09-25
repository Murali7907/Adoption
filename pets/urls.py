from django.urls import path
from . import views

urlpatterns = [
    # Core Public Pages
    path('', views.home_view, name='home'),
    path('explore/', views.pet_list_view, name='pet_list'),
    path('pet/<int:pet_id>/', views.pet_detail_view, name='pet_detail'),
    path('pet/detail/', views.pet_detail_view, name='pet_detail_sample'),
    path('add-pet/', views.add_pet_view, name='add_pet'),
    path('adopt/', views.adoption_form_view, name='adoption_form'),
    path('adopt/<int:pet_id>/', views.adoption_form_view, name='adoption_form_detail'),

    # Generic Dashboard Routing
    path('<str:role>-dashboard/', views.role_dashboard_view, name='role_dashboard_home'),
    path('<str:role>-dashboard/<str:page>/', views.role_dashboard_view, name='role_dashboard_page'),
]
