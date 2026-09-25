from django.contrib import admin
from .models import (
    Pet, AdoptionRequest, FavoritePet, TransportHub,
    DeliveryPartner, DeliveryRequest, DeliveryStatusHistory,
    HandoverVerification, PaymentTransaction, AuditLog
)

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'age', 'gender', 'shelter', 'status', 'approval_status', 'adoption_fee', 'created_at')
    list_filter = ('species', 'gender', 'status', 'approval_status', 'is_vaccinated', 'is_neutered')
    search_fields = ('name', 'breed', 'location', 'description')

@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'pet', 'shelter', 'status', 'request_date')
    list_filter = ('status', 'request_date')
    search_fields = ('customer__username', 'pet__name', 'shelter__shelter_name')

@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = ('partner_id', 'user', 'shelter', 'phone', 'vehicle_type', 'vehicle_number', 'rating', 'is_active')
    list_filter = ('is_active', 'vehicle_type')
    search_fields = ('partner_id', 'user__username', 'vehicle_number', 'phone')

@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'adoption_request', 'delivery_partner', 'status', 'priority', 'total_fee', 'payment_status', 'created_at')
    list_filter = ('status', 'priority', 'payment_status')
    search_fields = ('id', 'adoption_request__pet__name', 'delivery_partner__user__username')

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
