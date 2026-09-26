from django.shortcuts import render, redirect
from users.views import profile_view

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


# Generic Dashboard Router View - Delegates to profile_view for full Django backend hydration & active state tracking
def role_dashboard_view(request, role, page='dashboard'):
    # Normalize role and page names to prevent directory traversal
    role = role.lower().strip()
    page = page.lower().strip().replace('-', '_')
    
    valid_roles = ['admin', 'customer', 'shelter', 'delivery', 'adopter']
    if role not in valid_roles:
        return redirect('home')
        
    # Map 'customer' to 'adopter' for profile_view consistency
    target_role = 'adopter' if role == 'customer' else role
    
    # Mutate GET parameters on a copy of QueryDict so profile_view receives role & tab
    q_dict = request.GET.copy()
    q_dict['role'] = target_role
    if page and page != 'dashboard':
        q_dict['tab'] = page
    request.GET = q_dict
    
    return profile_view(request)

