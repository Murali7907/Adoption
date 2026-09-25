from django.shortcuts import render, redirect

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


# Generic Dashboard Router View
def role_dashboard_view(request, role, page='dashboard'):
    # Normalize role and page names to prevent directory traversal
    role = role.lower().strip()
    page = page.lower().strip().replace('-', '_')
    
    valid_roles = ['admin', 'customer', 'shelter', 'delivery']
    if role not in valid_roles:
        return redirect('home')
        
    return render(request, f'pets/{role}/{page}.html')
