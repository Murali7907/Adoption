from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

ROLE_CHOICES = (
    ('ADMIN', 'Admin'),
    ('CUSTOMER', 'Customer / Adopter'),
    ('SHELTER', 'Shelter'),
    ('DELIVERY', 'Delivery Staff'),
    ('VETERINARIAN', 'Veterinarian'),
)

SHELTER_STATUS_CHOICES = (
    ('PENDING', 'Pending Approval'),
    ('UNDER_REVIEW', 'Under Review'),
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
    state = models.CharField(max_length=100, blank=True, null=True, default='Kerala')
    postal_code = models.CharField(max_length=20, blank=True, null=True, default='682036')
    profile_photo = models.FileField(upload_to='profile_photos/', blank=True, null=True)
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Bi-directional sync with ShelterProfile if user is a shelter
        if self.role == 'SHELTER' and hasattr(self, 'user') and self.user and hasattr(self.user, 'shelter_profile'):
            shelter_prof = self.user.shelter_profile
            target_status = self.verification_status
            if self.is_verified and target_status != 'VERIFIED':
                target_status = 'VERIFIED'
            elif not self.is_verified and target_status == 'VERIFIED':
                target_status = 'PENDING'
            if shelter_prof.verification_status != target_status:
                shelter_prof.verification_status = target_status
                shelter_prof.save()

class ShelterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shelter_profile')
    shelter_name = models.CharField(max_length=150)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=SHELTER_STATUS_CHOICES, default='PENDING')
    location = models.CharField(max_length=100)
    shelter_type = models.CharField(max_length=100, default='Animal Rescue & Rehabilitation Center')
    address = models.CharField(max_length=255, default='Panampilly Nagar')
    city = models.CharField(max_length=100, default='Kochi')
    state = models.CharField(max_length=100, default='Kerala')
    logo = models.FileField(upload_to='shelter_logos/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    bio = models.TextField(blank=True, null=True)
    total_pets = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shelter_name} [{self.verification_status}]"

    def recalculate_verification_status(self, save=True):
        """
        Phase 12: Recalculates ShelterProfile verification status based on all associated documents.
        Enforces state consistency:
        - If no documents exist: preserve VERIFIED or SUSPENDED if already set by admin; otherwise PENDING.
        - If any document is REJECTED: status is REJECTED.
        - If all documents are VERIFIED (and at least one document exists): status is VERIFIED.
        - If any document is UNDER_REVIEW: status is UNDER_REVIEW.
        - Otherwise (e.g. documents exist, none rejected or under review, but some pending): status is PENDING.
        """
        all_docs = list(self.documents.all())
        if not all_docs:
            if self.verification_status not in ['VERIFIED', 'SUSPENDED']:
                self.verification_status = 'PENDING'
        else:
            if any(d.verification_status == 'REJECTED' for d in all_docs):
                self.verification_status = 'REJECTED'
            elif all(d.verification_status == 'VERIFIED' for d in all_docs):
                self.verification_status = 'VERIFIED'
            elif any(d.verification_status == 'UNDER_REVIEW' for d in all_docs):
                self.verification_status = 'UNDER_REVIEW'
            else:
                self.verification_status = 'PENDING'

        if save:
            self.save()
        return self.verification_status

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Bi-directional sync with UserProfile
        if hasattr(self, 'user') and self.user and hasattr(self.user, 'profile'):
            prof = self.user.profile
            needs_save = False
            expected_is_verified = (self.verification_status == 'VERIFIED')
            if prof.verification_status != self.verification_status:
                prof.verification_status = self.verification_status
                needs_save = True
            if prof.is_verified != expected_is_verified:
                prof.is_verified = expected_is_verified
                needs_save = True
            if expected_is_verified and not prof.verified_at:
                prof.verified_at = timezone.now()
                needs_save = True
            if needs_save:
                prof.save()

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


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    shelter = models.ForeignKey(ShelterProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username} [{self.created_at.strftime('%d %b %H:%M')}]"


# Phase 7: Shelter Document Upload Model
SHELTER_DOC_TYPE_CHOICES = (
    ('REGISTRATION', 'Shelter Registration / Proof'),
    ('GOVERNMENT_ID', 'Government / Identity Proof'),
    ('ADDRESS_PROOF', 'Address Proof'),
    ('AUTHORIZATION', 'Authorization Document'),
    ('ADOPTION_CERT', 'Adoption-Related Certification'),
    ('OTHER', 'Other Required Document'),
)

SHELTER_DOC_STATUS_CHOICES = (
    ('PENDING', 'Documents Pending'),
    ('UNDER_REVIEW', 'Under Review'),
    ('VERIFIED', 'Verified'),
    ('REJECTED', 'Rejected'),
)

class ShelterDocument(models.Model):
    shelter = models.ForeignKey(ShelterProfile, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_shelter_docs')
    doc_type = models.CharField(max_length=30, choices=SHELTER_DOC_TYPE_CHOICES, default='OTHER')
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='shelter_documents/')
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    upload_date = models.DateTimeField(auto_now_add=True)
    verification_status = models.CharField(max_length=20, choices=SHELTER_DOC_STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_shelter_docs')
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.shelter.shelter_name} [{self.verification_status}]"

    @property
    def file_size_display(self):
        sz = self.file_size
        if sz is None and self.file:
            try:
                sz = self.file.size
            except Exception:
                sz = None
        if sz is None:
            return "-"
        if sz < 1024:
            return f"{sz} B"
        elif sz < 1024 * 1024:
            return f"{sz / 1024:.1f} KB"
        else:
            return f"{sz / (1024 * 1024):.2f} MB"

    @property
    def stored_path(self):
        """Relative stored path within media storage."""
        return self.file.name if self.file else ''

    @property
    def exists_on_storage(self):
        """Check if file actually exists in physical storage."""
        if not self.file:
            return False
        try:
            return self.file.storage.exists(self.file.name)
        except Exception:
            return False

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.shelter_id:
            try:
                self.shelter.recalculate_verification_status(save=True)
            except Exception:
                pass

    def delete(self, *args, **kwargs):
        shelter = self.shelter
        res = super().delete(*args, **kwargs)
        if shelter:
            try:
                shelter.recalculate_verification_status(save=True)
            except Exception:
                pass
        return res


