from django.contrib import admin
from .models import (
    Pet, AdoptionRequest, FavoritePet, TransportHub,
    DeliveryPartner, DeliveryRequest, DeliveryStatusHistory,
    HandoverVerification, PaymentTransaction, AuditLog
)

class DeliveryStatusHistoryInline(admin.TabularInline):
    model = DeliveryStatusHistory
    extra = 0
    readonly_fields = ('previous_status', 'new_status', 'user', 'location', 'notes', 'timestamp')
    can_delete = False

class HandoverVerificationInline(admin.StackedInline):
    model = HandoverVerification
    extra = 0
    readonly_fields = ('otp_code', 'is_otp_verified', 'verified_at')

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'species', 'breed', 'age', 'gender', 'shelter', 'status', 'approval_status', 'adoption_fee', 'created_at')
    list_filter = ('shelter', 'species', 'gender', 'status', 'approval_status', 'is_vaccinated', 'is_neutered')
    search_fields = ('name', 'breed', 'location', 'description', 'shelter__shelter_name')
    list_editable = ('status', 'approval_status')
    ordering = ('-created_at',)

@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'get_customer_name', 'pet', 'shelter', 'status', 'request_date')
    list_filter = ('status', 'shelter', 'request_date')
    search_fields = ('customer__username', 'customer__first_name', 'customer__last_name', 'customer__email', 'pet__name', 'shelter__shelter_name')
    list_editable = ('status',)
    ordering = ('-request_date',)

    @admin.display(description='Customer Name')
    def get_customer_name(self, obj):
        name = obj.customer.get_full_name().strip() if obj.customer else ''
        return name if name else (obj.customer.username if obj.customer else '-')

@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = ('partner_id', 'user', 'get_full_name', 'get_plain_password', 'shelter', 'phone', 'vehicle_type', 'vehicle_number', 'availability_status', 'rating', 'is_active')
    list_filter = ('availability_status', 'is_active', 'shelter', 'vehicle_type')
    list_editable = ('availability_status', 'is_active')
    search_fields = ('partner_id', 'user__username', 'user__first_name', 'user__last_name', 'vehicle_number', 'phone', 'shelter__shelter_name')

    @admin.display(description='Driver Name')
    def get_full_name(self, obj):
        name = obj.user.get_full_name().strip() if obj.user else ''
        return name if name else (obj.user.username if obj.user else '-')

    @admin.display(description='Login Password')
    def get_plain_password(self, obj):
        if obj.user and hasattr(obj.user, 'profile') and obj.user.profile.plain_password:
            return obj.user.profile.plain_password
        return '123456'

@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'adoption_request', 'get_customer_name', 'get_pet_name', 'delivery_partner', 'status', 'priority', 'total_fee', 'payment_status', 'preferred_date', 'created_at')
    list_filter = ('status', 'priority', 'payment_status', 'created_at', 'delivery_partner')
    list_editable = ('delivery_partner', 'status', 'priority')
    search_fields = ('id', 'adoption_request__pet__name', 'adoption_request__customer__username', 'adoption_request__customer__first_name', 'adoption_request__shelter__shelter_name', 'delivery_partner__user__username')
    inlines = [DeliveryStatusHistoryInline, HandoverVerificationInline]
    ordering = ('-created_at',)

    @admin.display(description='Customer')
    def get_customer_name(self, obj):
        if obj.adoption_request and obj.adoption_request.customer:
            name = obj.adoption_request.customer.get_full_name().strip()
            return name if name else obj.adoption_request.customer.username
        return '-'

    @admin.display(description='Pet')
    def get_pet_name(self, obj):
        return obj.adoption_request.pet.name if (obj.adoption_request and obj.adoption_request.pet) else '-'

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'customer', 'total_amount', 'payment_method', 'status', 'refund_status', 'transaction_date')
    list_filter = ('status', 'refund_status', 'payment_method')
    search_fields = ('transaction_id', 'customer__username', 'gateway_ref')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_role', 'action', 'module', 'timestamp')
    list_filter = ('user_role', 'action', 'module')
    search_fields = ('description', 'user__username')

@admin.register(TransportHub)
class TransportHubAdmin(admin.ModelAdmin):
    list_display = ('hub_id', 'name', 'city', 'manager_name', 'contact_phone', 'is_active')
    list_filter = ('is_active', 'city')
    search_fields = ('name', 'city', 'manager_name')

@admin.register(FavoritePet)
class FavoritePetAdmin(admin.ModelAdmin):
    list_display = ('user', 'pet', 'created_at')

@admin.register(HandoverVerification)
class HandoverVerificationAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'otp_code', 'is_otp_verified', 'verified_at')

@admin.register(DeliveryStatusHistory)
class DeliveryStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'previous_status', 'new_status', 'user', 'timestamp')

