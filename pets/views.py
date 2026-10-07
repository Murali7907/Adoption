import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from users.views import profile_view, is_shelter_verified
from users.models import ShelterProfile, Message
from pets.models import DeliveryRequest, DeliveryPartner, Pet, AdoptionRequest, AuditLog
from django.contrib.auth.models import User
from django.db.models import Q

# Core Public Views
def home_view(request):
    return render(request, 'pets/home.html')

def pet_list_view(request):
    return render(request, 'pets/pet_list.html')

def pet_detail_view(request, pet_id=None):
    return render(request, 'pets/pet_detail.html')

def add_pet_view(request):
    # Phase 10 & 13: Gate pet creation until Admin verification
    shelter = None
    is_admin = False
    if request.user.is_authenticated:
        is_admin = bool(
            request.user.is_staff or 
            request.user.is_superuser or 
            (hasattr(request.user, 'profile') and str(request.user.profile.role).upper() == 'ADMIN')
        )
        shelter = getattr(request.user, 'shelter_profile', None) or (
            hasattr(request.user, 'profile') and str(request.user.profile.role).upper() == 'SHELTER' and
            ShelterProfile.objects.filter(user=request.user).first()
        )
        if not is_admin and shelter and not is_shelter_verified(shelter):
            if request.method == 'POST':
                return JsonResponse({
                    'success': False,
                    'error': 'Shelter verification is required before adding pets. Complete and submit your shelter documents for Admin verification before adding pets or delivery partners.'
                }, status=403)
            return redirect('/profile/#documents')
    else:
        if request.method == 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Shelter verification is required before adding pets.'
            }, status=403)
        return redirect('/users/login/?next=/pets/add/')

    if request.method == 'POST':
        name = request.POST.get('name') or request.POST.get('pet_name', '').strip()
        species = request.POST.get('species', 'Dog').strip()
        breed = request.POST.get('breed', '').strip()
        age = request.POST.get('age', '1 year').strip()
        description = request.POST.get('description', '').strip()
        image_url = request.POST.get('image_url', '').strip() or '/coco_beagle.jpg'
        
        if name and breed:
            pet = Pet.objects.create(
                name=name,
                species=species,
                breed=breed,
                age=age,
                description=description or f"{name} is a healthy, loving {breed} ready for adoption.",
                image_url=image_url,
                shelter=shelter,
                status='AVAILABLE',
                approval_status='APPROVED'
            )
            if shelter:
                shelter.total_pets = Pet.objects.filter(shelter=shelter).count()
                shelter.save()
        return redirect('/users/profile/?role=shelter#pets')
    return render(request, 'pets/add_pet.html')

def adoption_form_view(request, pet_id=None):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/users/login/?next=' + request.path)

        p_id = pet_id or request.POST.get('pet_id') or request.POST.get('petId') or 1
        clean_pet_id = str(p_id).replace('P', '').replace('PET-', '').strip()

        try:
            pet = Pet.objects.get(id=int(clean_pet_id))
        except (Pet.DoesNotExist, ValueError):
            pet = Pet.objects.first()

        if pet:
            shelter = pet.shelter or ShelterProfile.objects.first()
            customer = request.user
            notes = request.POST.get('reason') or request.POST.get('notes') or f"Adoption application submitted by {customer.get_full_name() or customer.username}."

            adoption_req, created = AdoptionRequest.objects.get_or_create(
                pet=pet,
                customer=customer,
                shelter=shelter,
                defaults={
                    'status': 'UNDER_REVIEW',
                    'notes': notes
                }
            )

            if not created and adoption_req.status in ['CANCELLED', 'REJECTED']:
                adoption_req.status = 'UNDER_REVIEW'
                adoption_req.save()

            pet.status = 'PENDING_ADOPTION'
            pet.save(update_fields=['status'])

            try:
                AuditLog.objects.create(
                    user=customer,
                    user_role='Adopter',
                    action='ADOPTION_REQUEST_CREATED',
                    module='Adoption Management',
                    adoption_request=adoption_req,
                    description=f"Adoption application #{adoption_req.id} submitted for pet '{pet.name}'."
                )

                cust_name = customer.get_full_name().strip() or customer.username
                cust_profile = getattr(customer, 'profile', None)
                cust_phone = getattr(cust_profile, 'phone', '') or customer.username
                cust_place = getattr(cust_profile, 'address', '') or "Kochi, Kerala"

                if shelter:
                    shelter_users = set()
                    if shelter.user:
                        shelter_users.add(shelter.user)
                    for u in User.objects.filter(Q(profile__role__iexact='SHELTER') | Q(shelter_profile=shelter)):
                        shelter_users.add(u)

                    for s_user in shelter_users:
                        Message.objects.create(
                            sender=customer,
                            recipient=s_user,
                            shelter=shelter,
                            subject=f"🐾 New Adoption Application #{adoption_req.id} for {pet.name}",
                            body=f"New adoption application #{adoption_req.id} received from customer '{cust_name}' (Phone: {cust_phone}, Location: {cust_place}) for pet '{pet.name}'. Review application and verify eligibility."
                        )

                admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(profile__role__iexact='ADMIN'))
                for admin_user in admins:
                    if admin_user != customer and (not shelter or admin_user != shelter.user):
                        Message.objects.create(
                            sender=customer,
                            recipient=admin_user,
                            shelter=shelter,
                            subject=f"🐾 New Adoption Application #{adoption_req.id} for {pet.name}",
                            body=f"New adoption application #{adoption_req.id} submitted by customer '{cust_name}' for pet '{pet.name}' at shelter '{shelter.shelter_name if shelter else 'Facility'}'."
                        )
            except Exception as e:
                print(f"Error creating adoption notification message: {e}")

        return redirect('/users/profile/?role=customer#orders')

    return render(request, 'pets/adoption_form.html')


# Generic Dashboard Router View - Delegates to specialized delivery views or profile_view with full hydration
def role_dashboard_view(request, role, page='dashboard'):
    # Normalize role and page names to prevent directory traversal
    role = role.lower().strip()
    page = page.lower().strip().replace('-', '_')
    
    valid_roles = ['admin', 'customer', 'shelter', 'delivery', 'adopter']
    if role not in valid_roles:
        return redirect('home')
        
    target_role = 'adopter' if role == 'customer' else role
    
    # Direct render for Delivery specific pages (dashboard, tracking, confirmation)
    if role == 'delivery' and page in ['dashboard', 'tracking', 'confirmation']:
        deliv_requests = []
        if request.user.is_authenticated:
            deliv_qs = DeliveryRequest.objects.filter(
                delivery_partner__user=request.user
            ).select_related(
                'adoption_request', 'adoption_request__pet', 
                'adoption_request__customer', 'adoption_request__shelter', 
                'delivery_partner', 'delivery_partner__user'
            ).order_by('-id')
        else:
            deliv_qs = DeliveryRequest.objects.all().select_related(
                'adoption_request', 'adoption_request__pet', 
                'adoption_request__customer', 'adoption_request__shelter', 
                'delivery_partner', 'delivery_partner__user'
            ).order_by('-id')

        for dr in deliv_qs:
            pet_obj = dr.adoption_request.pet if (dr.adoption_request and dr.adoption_request.pet) else None
            cust_user = dr.adoption_request.customer if dr.adoption_request else None
            sh_obj = dr.adoption_request.shelter if dr.adoption_request else None
            driver_user = dr.delivery_partner.user if dr.delivery_partner else None

            deliv_requests.append({
                'id': f"DEL-{dr.id}",
                'db_id': dr.id,
                'appId': f"KH102{dr.adoption_request.id:02d}" if dr.adoption_request else f"KH102{dr.id:02d}",
                'petId': f"P{pet_obj.id}" if pet_obj else "P00",
                'petName': pet_obj.name if pet_obj else "Pet",
                'petBreed': pet_obj.breed if pet_obj else "N/A",
                'petSpecies': pet_obj.species if pet_obj else "N/A",
                'petImage': pet_obj.image_url if pet_obj else "",
                'customerName': cust_user.get_full_name() or cust_user.username if cust_user else "Adopter",
                'customerPhone': getattr(getattr(cust_user, 'profile', None), 'phone', '') if cust_user else "",
                'dropAddress': dr.drop_address or "",
                'shelterName': sh_obj.shelter_name if sh_obj else "Shelter Facility",
                'shelterLocation': sh_obj.location if sh_obj else "",
                'shelterPhone': sh_obj.phone if sh_obj else "",
                'agent': driver_user.get_full_name() or driver_user.username if driver_user else "Unassigned Driver",
                'agentId': dr.delivery_partner.partner_id if dr.delivery_partner else "DP-00",
                'status': dr.status,
                'statusDisplay': dr.get_status_display() if hasattr(dr, 'get_status_display') else dr.status,
                'preferredDate': dr.preferred_date.strftime("%d %b %Y") if dr.preferred_date else "",
                'proofUrl': dr.proof_photo_url or "",
                'totalFee': float(dr.total_fee) if dr.total_fee else 0.0
            })

        driver_partner = DeliveryPartner.objects.filter(user=request.user).first() if request.user.is_authenticated else None

        ctx = {
            'deliv_requests': deliv_requests,
            'db_delivery_requests_json': json.dumps(deliv_requests),
            'driver_partner': driver_partner,
            'current_role': 'delivery',
            'active_tab': page
        }

        if page == 'tracking':
            return render(request, 'pets/delivery/tracking.html', ctx)
        elif page == 'confirmation':
            return render(request, 'pets/delivery/confirmation.html', ctx)
        else:
            return render(request, 'pets/delivery/dashboard.html', ctx)

    # Fallback/delegation to profile_view
    q_dict = request.GET.copy()
    q_dict['role'] = target_role
    if page and page != 'dashboard':
        q_dict['tab'] = page
    request.GET = q_dict
    
    return profile_view(request)


