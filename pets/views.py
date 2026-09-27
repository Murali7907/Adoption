import json
from django.shortcuts import render, redirect
from users.views import profile_view
from pets.models import DeliveryRequest, DeliveryPartner, Pet

# Core Public Views
def home_view(request):
    return render(request, 'pets/home.html')

def pet_list_view(request):
    return render(request, 'pets/pet_list.html')

def pet_detail_view(request, pet_id=None):
    return render(request, 'pets/pet_detail.html')

def add_pet_view(request):
    if request.method == 'POST':
        return redirect('shelter_pets')
    return render(request, 'pets/add_pet.html')

def adoption_form_view(request, pet_id=None):
    if request.method == 'POST':
        return redirect('customer_requests')
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
                'petId': f"P{pet_obj.id}" if pet_obj else "P101",
                'petName': pet_obj.name if pet_obj else "Companion Pet",
                'petBreed': pet_obj.breed if pet_obj else "Mixed Breed",
                'petSpecies': pet_obj.species if pet_obj else "Dog",
                'petImage': pet_obj.image_url if pet_obj else "/kindheart_bruno.jpg",
                'customerName': cust_user.get_full_name() or cust_user.username if cust_user else "Adopter",
                'customerPhone': getattr(getattr(cust_user, 'profile', None), 'phone', '+91 98470 12345') if cust_user else "+91 98470 12345",
                'dropAddress': dr.drop_address or "Adopter Location, Kochi, Kerala",
                'shelterName': sh_obj.shelter_name if sh_obj else "Happy Paws Shelter",
                'shelterLocation': sh_obj.location if sh_obj else "Kochi Center",
                'shelterPhone': sh_obj.phone if sh_obj else "+91 98450 11223",
                'agent': driver_user.get_full_name() or driver_user.username if driver_user else "Unassigned Driver",
                'agentId': dr.delivery_partner.partner_id if dr.delivery_partner else "DP-101",
                'status': dr.status,
                'statusDisplay': dr.get_status_display() if hasattr(dr, 'get_status_display') else dr.status,
                'preferredDate': dr.preferred_date.strftime("%d %b %Y") if dr.preferred_date else "Today",
                'proofUrl': dr.proof_photo_url or "",
                'totalFee': float(dr.total_fee) if dr.total_fee else 1100.0
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


