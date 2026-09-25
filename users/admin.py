from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, ShelterProfile

@admin.action(description="Verify & Approve selected profiles")
def approve_profiles(modeladmin, request, queryset):
    updated = queryset.update(
        is_verified=True,
        verification_status='VERIFIED',
        verified_at=timezone.now()
    )
    modeladmin.message_user(request, f"{updated} profile(s) have been verified and approved successfully.")

@admin.action(description="Reject selected profiles")
def reject_profiles(modeladmin, request, queryset):
    updated = queryset.update(
        is_verified=False,
        verification_status='REJECTED'
    )
    modeladmin.message_user(request, f"{updated} profile(s) have been marked as REJECTED.")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'get_email',
        'get_full_name',
        'role',
        'phone',
        'verification_status',
        'is_verified',
        'created_at'
    )
    list_filter = ('verification_status', 'is_verified', 'role', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone', 'address')
    list_editable = ('verification_status', 'is_verified')
    actions = [approve_profiles, reject_profiles]
    ordering = ('-created_at',)

    @admin.display(description='Email', ordering='user__email')
    def get_email(self, obj):
        return obj.user.email

    @admin.display(description='Full Name', ordering='user__first_name')
    def get_full_name(self, obj):
        name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return name if name else obj.user.username


@admin.action(description="Verify & Approve selected shelters")
def approve_shelters(modeladmin, request, queryset):
    updated = queryset.update(verification_status='VERIFIED')
    for shelter in queryset:
        if hasattr(shelter.user, 'profile'):
            shelter.user.profile.is_verified = True
            shelter.user.profile.verification_status = 'VERIFIED'
            shelter.user.profile.save()
    modeladmin.message_user(request, f"{updated} shelter profile(s) verified successfully.")

@admin.action(description="Reject selected shelters")
def reject_shelters(modeladmin, request, queryset):
    updated = queryset.update(verification_status='REJECTED')
    for shelter in queryset:
        if hasattr(shelter.user, 'profile'):
            shelter.user.is_verified = False
            shelter.user.verification_status = 'REJECTED'
            shelter.user.save()
    modeladmin.message_user(request, f"{updated} shelter profile(s) rejected.")

@admin.register(ShelterProfile)
class ShelterProfileAdmin(admin.ModelAdmin):
    list_display = (
        'shelter_name',
        'user',
        'location',
        'phone',
        'verification_status',
        'total_pets',
        'created_at'
    )
    list_filter = ('verification_status', 'location', 'created_at')
    search_fields = ('shelter_name', 'user__username', 'user__email', 'location', 'license_number')
    list_editable = ('verification_status',)
    actions = [approve_shelters, reject_shelters]
    ordering = ('-created_at',)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'KindHeart Profile'
    fk_name = 'user'
    fields = ('role', 'phone', 'address', 'verification_status', 'is_verified', 'verified_at')

class KindHeartUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_verification_status', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role', 'profile__verification_status')

    @admin.display(description='Role', ordering='profile__role')
    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else '-'

    @admin.display(description='Verification Status', ordering='profile__verification_status')
    def get_verification_status(self, obj):
        return obj.profile.verification_status if hasattr(obj, 'profile') else '-'

# Re-register User with customized KindHeartUserAdmin
admin.site.unregister(User)
admin.site.register(User, KindHeartUserAdmin)
