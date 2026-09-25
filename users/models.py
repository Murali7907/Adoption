from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = (
    ('ADMIN', 'Admin'),
    ('CUSTOMER', 'Customer / Adopter'),
    ('SHELTER', 'Shelter'),
    ('DELIVERY', 'Delivery Staff'),
    ('VETERINARIAN', 'Veterinarian'),
)

SHELTER_STATUS_CHOICES = (
    ('PENDING', 'Pending Approval'),
    ('VERIFIED', 'Verified'),
    ('REJECTED', 'Rejected'),
    ('SUSPENDED', 'Suspended'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    dob = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    occupation = models.CharField(max_length=150, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    residence_type = models.CharField(max_length=150, blank=True, null=True)
    home_ownership = models.CharField(max_length=150, blank=True, null=True)
    id_document = models.FileField(upload_to='user_documents/', blank=True, null=True)
    id_document_name = models.CharField(max_length=255, blank=True, null=True)
    address_document = models.FileField(upload_to='user_documents/', blank=True, null=True)
    address_document_name = models.CharField(max_length=255, blank=True, null=True)
    residence_document = models.FileField(upload_to='user_documents/', blank=True, null=True)
    residence_document_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, choices=SHELTER_STATUS_CHOICES, default='PENDING')
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role}) [{self.verification_status}]"

class ShelterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shelter_profile')
    shelter_name = models.CharField(max_length=150)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=SHELTER_STATUS_CHOICES, default='PENDING')
    location = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    bio = models.TextField(blank=True, null=True)
    total_pets = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shelter_name} [{self.verification_status}]"

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key} = {self.value}"

class RolePermission(models.Model):
    role = models.CharField(max_length=50)  # e.g., 'admin', 'shelter', 'adopter', 'delivery'
    permission_key = models.CharField(max_length=100)
    is_granted = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('role', 'permission_key')

    def __str__(self):
        return f"{self.role} - {self.permission_key}: {self.is_granted}"

