from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import ShelterProfile

PET_APPROVAL_CHOICES = (
    ('PENDING_APPROVAL', 'Pending Admin Approval'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
)

PET_STATUS_CHOICES = (
    ('AVAILABLE', 'Available'),
    ('PENDING_ADOPTION', 'Pending Adoption'),
    ('ADOPTED', 'Adopted'),
)

ADOPTION_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('UNDER_REVIEW', 'Under Review'),
    ('APPROVED', 'Approved'),
    ('DELIVERY_SCHEDULED', 'Delivery Scheduled'),
    ('DELIVERED', 'Delivered'),
    ('COMPLETED', 'Completed'),
    ('REJECTED', 'Rejected'),
)

DELIVERY_STATUS_CHOICES = (
    ('ADOPTION_APPROVED', 'Adoption Approved'),
    ('DELIVERY_REQUESTED', 'Delivery Requested'),
    ('ELIGIBILITY_CHECKED', 'Eligibility Checked'),
    ('DELIVERY_CREATED', 'Delivery Created'),
    ('SCHEDULED', 'Delivery Scheduled'),
    ('PARTNER_ASSIGNED', 'Partner Assigned'),
    ('PICKUP_SCHEDULED', 'Pickup Scheduled'),
    ('PET_READY', 'Pet Ready for Pickup'),
    ('PICKUP_CONFIRMED', 'Pickup Confirmed'),
    ('PET_PICKED_UP', 'Pet Picked Up'),
    ('ORIGIN_HUB', 'Origin Hub / Transport Center'),
    ('IN_TRANSIT', 'In Transit'),
    ('DESTINATION_HUB', 'Destination Hub'),
    ('OUT_FOR_DELIVERY', 'Out for Delivery'),
    ('NEAR_DESTINATION', 'Near Destination'),
    ('ARRIVED', 'Arrived at Destination'),
    ('HANDOVER_PENDING', 'Handover Verification Pending'),
    ('COMPLETED', 'Delivery Completed'),
    ('FAILED', 'Failed Delivery'),
    ('CANCELLED', 'Cancelled'),
)

PAYMENT_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('PROCESSING', 'Processing'),
    ('SUCCESSFUL', 'Successful'),
    ('FAILED', 'Failed'),
    ('CANCELLED', 'Cancelled'),
    ('REFUNDED', 'Refunded'),
    ('PARTIALLY_REFUNDED', 'Partially Refunded'),
)

REFUND_STATUS_CHOICES = (
    ('NONE', 'No Refund'),
    ('INITIATED', 'Refund Initiated'),
    ('COMPLETED', 'Refund Completed'),
    ('FAILED', 'Refund Failed'),
)

AUDIT_ACTION_CHOICES = (
    ('ADOPTION_SUBMITTED', 'Adoption Request Submitted'),
    ('REQUEST_REVIEWED', 'Request Moved to Review'),
    ('REQUEST_APPROVED', 'Request Approved'),
    ('REQUEST_REJECTED', 'Request Rejected'),
    ('PAYMENT_INITIATED', 'Payment Initiated'),
    ('PAYMENT_SUCCESSFUL', 'Payment Successful'),
    ('PAYMENT_FAILED', 'Payment Failed'),
    ('REFUND_PROCESSED', 'Refund Processed'),
    ('DRIVER_ASSIGNED', 'Delivery Driver Assigned'),
    ('PET_PICKED_UP', 'Pet Picked Up from Shelter'),
    ('PET_DELIVERED', 'Pet Delivered to Adopter'),
    ('ADOPTION_COMPLETED', 'Adoption Completed'),
    ('REQUEST_CANCELLED', 'Request Cancelled'),
)

# 1. 🐕 PET MODEL
class Pet(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50) # Dog, Cat, Bird, Rabbit
    breed = models.CharField(max_length=100)
    age = models.CharField(max_length=50)
    gender = models.CharField(max_length=10) # Male, Female
    weight = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100)
    description = models.TextField()
    medical_history = models.TextField(blank=True, null=True)
    is_vaccinated = models.BooleanField(default=True)
    is_neutered = models.BooleanField(default=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    shelter = models.ForeignKey(ShelterProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='listed_pets')
    
    approval_status = models.CharField(max_length=20, choices=PET_APPROVAL_CHOICES, default='APPROVED')
    status = models.CharField(max_length=20, choices=PET_STATUS_CHOICES, default='AVAILABLE')
    adoption_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.species} - {self.breed})"

# 2. 📋 ADOPTION REQUEST MODEL
class AdoptionRequest(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='adoption_requests')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_adoption_requests')
    shelter = models.ForeignKey(ShelterProfile, on_delete=models.CASCADE, related_name='shelter_adoption_requests')
    request_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=25, choices=ADOPTION_STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.customer.username} -> {self.pet.name} [{self.status}]"

class FavoritePet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pet')

# 3. 🏢 TRANSPORT LOGISTICS HUBS MODEL
class TransportHub(models.Model):
    hub_id = models.CharField(max_length=50, unique=True, default='HUB-101')
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    manager_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    capacity = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.city}) [{self.hub_id}]"

# 4. 🚚 DELIVERY PARTNER MODEL
class DeliveryPartner(models.Model):
    partner_id = models.CharField(max_length=50, unique=True, default='DP-1001')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_partner_profile')
    shelter = models.ForeignKey(ShelterProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_partners')
    phone = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=50, default='Pet Taxi Van') # Pet Taxi Van, Express Van, Courier
    vehicle_number = models.CharField(max_length=30)
    license_verified = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.80)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.vehicle_number}) [{self.partner_id}]"

# 5. 🚚 LOGISTICS SHIPMENT DELIVERY MODEL
class DeliveryRequest(models.Model):
    adoption_request = models.OneToOneField(AdoptionRequest, on_delete=models.CASCADE, related_name='delivery')
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_deliveries')
    origin_hub = models.ForeignKey(TransportHub, on_delete=models.SET_NULL, null=True, blank=True, related_name='origin_deliveries')
    destination_hub = models.ForeignKey(TransportHub, on_delete=models.SET_NULL, null=True, blank=True, related_name='destination_deliveries')
    
    pickup_address = models.TextField(default='Shelter Address')
    drop_address = models.TextField(default='Adopter Address')
    preferred_date = models.DateField(default=timezone.now)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    
    priority = models.CharField(max_length=20, default='NORMAL') # URGENT, NORMAL, EXPRESS
    status = models.CharField(max_length=30, choices=DELIVERY_STATUS_CHOICES, default='IN_TRANSIT')
    
    base_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    distance_fee = models.DecimalField(max_digits=10, decimal_places=2, default=300.00)
    pet_transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)
    special_handling_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1100.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='SUCCESSFUL')
    
    proof_photo_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery #DEL-{self.id} for {self.adoption_request.pet.name} [{self.status}]"

# 6. 📜 CHRONOLOGICAL AUDIT TIMELINE MODEL
class DeliveryStatusHistory(models.Model):
    delivery = models.ForeignKey(DeliveryRequest, on_delete=models.CASCADE, related_name='history_events')
    previous_status = models.CharField(max_length=30)
    new_status = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"History #{self.id}: {self.previous_status} -> {self.new_status} at {self.timestamp}"

# 7. ✍️ HANDOVER VERIFICATION MODEL
class HandoverVerification(models.Model):
    delivery = models.OneToOneField(DeliveryRequest, on_delete=models.CASCADE, related_name='handover_verification')
    otp_code = models.CharField(max_length=10, default='4892')
    is_otp_verified = models.BooleanField(default=False)
    digital_signature_data = models.TextField(blank=True, null=True)
    photo_proof_url = models.URLField(max_length=500, blank=True, null=True)
    handover_notes = models.TextField(blank=True, null=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Handover Verification for Delivery #{self.delivery.id} [Verified: {self.is_otp_verified}]"

# 8. 💳 FINANCIAL PAYMENT TRANSACTION MODEL
class PaymentTransaction(models.Model):
    transaction_id = models.CharField(max_length=50, unique=True, default='TXN-2026-1001')
    adoption_request = models.ForeignKey(AdoptionRequest, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_payments', null=True, blank=True)
    adoption_fee = models.DecimalField(max_digits=10, decimal_places=2, default=3500.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1100.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=4600.00)
    payment_method = models.CharField(max_length=50, default='UPI / GooglePay') # UPI, Credit Card, NetBanking, PayPal
    payment_gateway = models.CharField(max_length=50, default='Razorpay') # Razorpay, Stripe, PayPal
    gateway_ref = models.CharField(max_length=100, default='pay_NxF928172635')
    status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default='SUCCESSFUL')
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='NONE')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    invoice_url = models.URLField(max_length=500, blank=True, null=True)
    transaction_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transaction #{self.transaction_id} - ₹{self.total_amount} [{self.status}]"

# 9. 🔍 SYSTEM AUDIT LOG MODEL
class AuditLog(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_actions')
    user_role = models.CharField(max_length=50, default='Admin') # Admin, Shelter, Customer, Driver, System
    action = models.CharField(max_length=50, choices=AUDIT_ACTION_CHOICES, default='ADOPTION_SUBMITTED')
    module = models.CharField(max_length=50, default='Adoption Requests') # Adoption Requests, Payments, Delivery, User Management, System
    adoption_request = models.ForeignKey(AdoptionRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    previous_status = models.CharField(max_length=50, blank=True, null=True)
    new_status = models.CharField(max_length=50, blank=True, null=True)
    ip_address = models.CharField(max_length=45, default='127.0.0.1')
    device_info = models.CharField(max_length=150, default='Chrome 122.0 (Windows 11)')
    description = models.TextField()

    def __str__(self):
        return f"AuditLog #{self.id}: {self.action} by {self.user_role} at {self.timestamp}"
