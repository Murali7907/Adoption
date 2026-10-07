from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, ShelterProfile, SystemSetting, RolePermission, Message, ShelterDocument

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_at')
    search_fields = ('key', 'value')

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission_key', 'is_granted', 'updated_at')
    list_filter = ('role', 'is_granted')
    search_fields = ('role', 'permission_key')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'shelter', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'body')


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

@admin.action(description="Deactivate selected accounts")
def deactivate_accounts(modeladmin, request, queryset):
    count = 0
    from pets.models import AuditLog
    for item in queryset:
        if isinstance(item, User):
            user = item
            prof = getattr(user, 'profile', None)
            sp = getattr(user, 'shelter_profile', None)
        elif isinstance(item, UserProfile):
            prof = item
            user = item.user
            sp = getattr(user, 'shelter_profile', None)
        elif isinstance(item, ShelterProfile):
            sp = item
            user = item.user
            prof = getattr(user, 'profile', None)
        else:
            continue

        if user.is_superuser:
            continue

        user.is_active = False
        user.save()
        if prof:
            prof.is_active = False
            prof.verification_status = 'SUSPENDED'
            prof.save()
        if sp:
            sp.verification_status = 'SUSPENDED'
            sp.save()
        if hasattr(user, 'delivery_partner_profile'):
            dp = user.delivery_partner_profile
            dp.is_active = False
            dp.save()

        try:
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                user_role='Admin',
                action='ACCOUNT_DEACTIVATED',
                module='User Management',
                description=f"Account '{user.username}' deactivated by Admin from Django Backend Admin panel."
            )
        except Exception:
            pass
        count += 1
    modeladmin.message_user(request, f"{count} account(s) deactivated successfully.")

@admin.action(description="Activate selected accounts")
def activate_accounts(modeladmin, request, queryset):
    count = 0
    from pets.models import AuditLog
    for item in queryset:
        if isinstance(item, User):
            user = item
            prof = getattr(user, 'profile', None)
            sp = getattr(user, 'shelter_profile', None)
        elif isinstance(item, UserProfile):
            prof = item
            user = item.user
            sp = getattr(user, 'shelter_profile', None)
        elif isinstance(item, ShelterProfile):
            sp = item
            user = item.user
            prof = getattr(user, 'profile', None)
        else:
            continue

        user.is_active = True
        user.save()
        if prof:
            prof.is_active = True
            prof.is_verified = True
            prof.verification_status = 'VERIFIED'
            prof.save()
        if sp:
            sp.verification_status = 'VERIFIED'
            sp.save()
        if hasattr(user, 'delivery_partner_profile'):
            dp = user.delivery_partner_profile
            dp.is_active = True
            dp.save()

        try:
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                user_role='Admin',
                action='ACCOUNT_ACTIVATED',
                module='User Management',
                description=f"Account '{user.username}' activated by Admin from Django Backend Admin panel."
            )
        except Exception:
            pass
        count += 1
    modeladmin.message_user(request, f"{count} account(s) activated successfully.")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'get_email',
        'get_full_name',
        'role',
        'phone',
        'plain_password',
        'is_active',
        'verification_status',
        'is_verified',
        'created_at'
    )
    list_filter = ('is_active', 'verification_status', 'is_verified', 'role', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone', 'address', 'plain_password')
    list_editable = ('is_active', 'verification_status', 'is_verified')
    actions = [activate_accounts, deactivate_accounts, approve_profiles, reject_profiles]
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
    count = 0
    for shelter in queryset:
        shelter.verification_status = 'VERIFIED'
        shelter.save()
        count += 1
    modeladmin.message_user(request, f"{count} shelter profile(s) verified successfully.")

@admin.action(description="Reject selected shelters")
def reject_shelters(modeladmin, request, queryset):
    count = 0
    for shelter in queryset:
        shelter.verification_status = 'REJECTED'
        shelter.save()
        count += 1
    modeladmin.message_user(request, f"{count} shelter profile(s) rejected.")

class ShelterDocumentInline(admin.TabularInline):
    model = ShelterDocument
    extra = 0
    fields = ('doc_type', 'original_filename', 'file_size_display', 'verification_status', 'upload_date', 'view_file_link')
    readonly_fields = ('original_filename', 'doc_type', 'upload_date', 'file_size_display', 'view_file_link')
    can_delete = True

    @admin.display(description='Stored File')
    def view_file_link(self, obj):
        if obj and obj.file:
            from django.utils.html import format_html
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">View File</a>', obj.file.url)
        return '-'

@admin.register(ShelterProfile)
class ShelterProfileAdmin(admin.ModelAdmin):
    list_display = (
        'shelter_name',
        'user',
        'get_plain_password',
        'location',
        'phone',
        'verification_status',
        'total_pets',
        'created_at'
    )
    list_filter = ('verification_status', 'location', 'created_at')
    search_fields = ('shelter_name', 'user__username', 'user__email', 'location', 'license_number')
    list_editable = ('verification_status',)
    inlines = [ShelterDocumentInline]
    actions = [activate_accounts, deactivate_accounts, approve_shelters, reject_shelters]
    ordering = ('-created_at',)

    @admin.display(description='Login Password', ordering='user__profile__plain_password')
    def get_plain_password(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.plain_password:
            return obj.user.profile.plain_password
        return '123456'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if hasattr(obj, 'user') and obj.user and hasattr(obj.user, 'profile'):
            prof = obj.user.profile
            is_ver = (obj.verification_status == 'VERIFIED')
            if prof.verification_status != obj.verification_status or prof.is_verified != is_ver:
                prof.verification_status = obj.verification_status
                prof.is_verified = is_ver
                if is_ver and not prof.verified_at:
                    prof.verified_at = timezone.now()
                prof.save()

    def delete_model(self, request, obj):
        user = obj.user
        super().delete_model(request, obj)
        if user and not user.is_superuser:
            try:
                user.delete()
            except Exception:
                pass

    def delete_queryset(self, request, queryset):
        users_to_delete = [s.user for s in queryset if s.user and not s.user.is_superuser]
        super().delete_queryset(request, queryset)
        for u in users_to_delete:
            try:
                u.delete()
            except Exception:
                pass

@admin.action(description="Verify & Approve selected documents")
def verify_documents(modeladmin, request, queryset):
    now = timezone.now()
    count = 0
    affected_shelters = set()
    for doc in queryset:
        doc.verification_status = 'VERIFIED'
        doc.reviewed_by = request.user
        doc.review_date = now
        doc.save()
        count += 1
        if doc.shelter:
            affected_shelters.add(doc.shelter)
    for sh in affected_shelters:
        sh.recalculate_verification_status(save=True)
    modeladmin.message_user(request, f"{count} document(s) marked as VERIFIED.")

@admin.action(description="Mark selected documents as UNDER REVIEW")
def mark_documents_under_review(modeladmin, request, queryset):
    now = timezone.now()
    count = 0
    affected_shelters = set()
    for doc in queryset:
        doc.verification_status = 'UNDER_REVIEW'
        doc.reviewed_by = request.user
        doc.review_date = now
        doc.save()
        count += 1
        if doc.shelter:
            affected_shelters.add(doc.shelter)
    for sh in affected_shelters:
        sh.recalculate_verification_status(save=True)
    modeladmin.message_user(request, f"{count} document(s) marked as UNDER REVIEW.")

@admin.action(description="Reject selected documents")
def reject_documents(modeladmin, request, queryset):
    now = timezone.now()
    count = 0
    affected_shelters = set()
    for doc in queryset:
        doc.verification_status = 'REJECTED'
        doc.reviewed_by = request.user
        doc.review_date = now
        doc.save()
        count += 1
        if doc.shelter:
            affected_shelters.add(doc.shelter)
    for sh in affected_shelters:
        sh.recalculate_verification_status(save=True)
    modeladmin.message_user(request, f"{count} document(s) marked as REJECTED.")

@admin.register(ShelterDocument)
class ShelterDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'shelter',
        'doc_type',
        'original_filename',
        'file_size_display',
        'verification_status',
        'uploaded_by',
        'upload_date',
        'view_file_link',
        'reviewed_by',
        'review_date',
    )
    list_filter = ('verification_status', 'doc_type', 'upload_date')
    search_fields = ('shelter__shelter_name', 'original_filename', 'uploaded_by__username', 'review_notes')
    readonly_fields = ('upload_date', 'view_file_link', 'file_size_display')
    actions = [verify_documents, mark_documents_under_review, reject_documents]
    ordering = ('-upload_date',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.shelter:
            obj.shelter.recalculate_verification_status(save=True)

    def delete_model(self, request, obj):
        shelter = obj.shelter
        super().delete_model(request, obj)
        if shelter:
            shelter.recalculate_verification_status(save=True)

    @admin.display(description='Stored File')
    def view_file_link(self, obj):
        if obj.file:
            from django.utils.html import format_html
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">View File</a>', obj.file.url)
        return '-'



class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'KindHeart Profile'
    fk_name = 'user'
    fields = ('role', 'phone', 'plain_password', 'address', 'verification_status', 'is_verified', 'verified_at')

class KindHeartUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_plain_password', 'get_verification_status', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role', 'profile__verification_status')
    actions = [activate_accounts, deactivate_accounts]

    @admin.display(description='Role', ordering='profile__role')
    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else '-'

    @admin.display(description='Login Password', ordering='profile__plain_password')
    def get_plain_password(self, obj):
        if hasattr(obj, 'profile') and obj.profile.plain_password:
            return obj.profile.plain_password
        return '123456'

    @admin.display(description='Verification Status', ordering='profile__verification_status')
    def get_verification_status(self, obj):
        return obj.profile.verification_status if hasattr(obj, 'profile') else '-'

# Re-register User with customized KindHeartUserAdmin
admin.site.unregister(User)
admin.site.register(User, KindHeartUserAdmin)
