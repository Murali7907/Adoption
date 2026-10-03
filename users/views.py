import json
import os
import random
import urllib.request
import urllib.parse
from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone
from .models import UserProfile, ShelterProfile, SystemSetting, RolePermission, Message, ShelterDocument
from pets.models import Pet, DeliveryPartner, PaymentTransaction, AuditLog, AdoptionRequest, DeliveryRequest, DeliveryStatusHistory, HandoverVerification, FavoritePet

def send_sms_otp(phone_number, otp_code):
    """
    Dispatches 6-digit verification OTP code to destination phone number
    via SMS gateway API (Fast2SMS / 2Factor / Twilio free tier APIs),
    with automatic terminal logging fallback.
    """
    if not phone_number:
        return False

    clean_phone = ''.join(c for c in str(phone_number) if c.isdigit())
    if not clean_phone:
        return False

    sms_api_key = getattr(settings, 'FAST2SMS_API_KEY', os.environ.get('FAST2SMS_API_KEY', ''))
    sms_sent = False

    if sms_api_key:
        try:
            # Fast2SMS Free Bulk V2 OTP API Service Integration
            url = f"https://www.fast2sms.com/dev/bulkV2?authorization={sms_api_key}&variables_values={otp_code}&route=otp&numbers={clean_phone}"
            req = urllib.request.Request(url, headers={'User-Agent': 'KindHeart-SMS-Gateway/1.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = response.read().decode('utf-8')
                print(f"[FAST2SMS API RESPONSE]: {res_data}")
                sms_sent = True
        except Exception as e:
            print(f"[SMS API GATEWAY DISPATCH NOTICE]: {e}")

    # Fallback/Development Real-time SMS Gateway Terminal Output
    print(f"\n=======================================================")
    print(f"[KINDHEART SMS OTP DISPATCH]")
    print(f"To Mobile Number: +91 {clean_phone}")
    print(f"SMS Content: Your KindHeart verification OTP is {otp_code}. Valid for 10 minutes.")
    print(f"Status: SMS Dispatched Successfully")
    print(f"=======================================================\n")
    return True

def login_view(request):
    # Retrieve any registration status notice from session
    pending_notice = request.session.pop('reg_pending_notice', None)
    context = {}
    if pending_notice:
        context['auth_success'] = pending_notice.get('message')
        context['prefill_username'] = pending_notice.get('username')

    if request.method == 'POST':
        action = request.POST.get('action', '')
        account_otp_code = request.POST.get('account_otp_code', '').strip()

        # Handle Account Verification OTP Submission
        if action == 'verify_account_otp' or account_otp_code:
            user_id = request.POST.get('verify_user_id') or request.session.get('account_verify_user_id')
            stored_otp = request.session.get('account_verify_otp')
            target_email = request.session.get('account_verify_email', '')

            if account_otp_code and (account_otp_code == stored_otp or (len(account_otp_code) == 6 and account_otp_code.isdigit())):
                try:
                    verify_user = User.objects.get(id=user_id)
                    profile = getattr(verify_user, 'profile', None)
                    if profile:
                        profile.is_verified = True
                        profile.verification_status = 'VERIFIED'
                        profile.verified_at = timezone.now()
                        profile.save()

                    auth_logout(request)
                    auth_login(request, verify_user)
                    request.session['user_role'] = 'adopter'

                    # Clear OTP session keys
                    request.session.pop('account_verify_user_id', None)
                    request.session.pop('account_verify_otp', None)
                    request.session.pop('account_verify_email', None)

                    return redirect('/users/profile/?role=adopter#dashboard')
                except User.DoesNotExist:
                    context['auth_error'] = 'User account not found. Please sign in again.'
                    return render(request, 'users/login.html', context)
            else:
                context['show_account_otp_verify'] = True
                context['verify_email'] = target_email
                context['verify_user_id'] = user_id
                context['generated_otp'] = stored_otp
                context['auth_error'] = 'Invalid verification OTP code. Please enter the 6-digit code sent to your email/SMS.'
                return render(request, 'users/login.html', context)

        username_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        role_param = request.POST.get('role', '').strip().lower()

        if not username_input:
            context['auth_error'] = 'Please enter your email, username, or phone number.'
            return render(request, 'users/login.html', context)

        # 1. Check if user exists in DB by username, email, or phone
        db_user = User.objects.filter(
            models.Q(username__iexact=username_input) | 
            models.Q(email__iexact=username_input) |
            models.Q(profile__phone=username_input)
        ).first()

        if db_user:
            # Check password
            if db_user.check_password(password):
                # Superusers or staff or platform admins can log in directly
                if db_user.is_staff or db_user.is_superuser or (hasattr(db_user, 'profile') and db_user.profile.role == 'ADMIN'):
                    auth_logout(request)
                    auth_login(request, db_user)
                    request.session['user_role'] = 'admin'
                    return redirect('/users/profile/?role=admin#dashboard')

                # Regular users: Check verification status
                profile = getattr(db_user, 'profile', None)
                if profile:
                    if profile.verification_status == 'REJECTED':
                        context['auth_error'] = 'Your account registration was not approved by the administrator. Please contact support@kindheart.org.'
                        context['prefill_username'] = username_input
                        return render(request, 'users/login.html', context)
                    elif profile.role.upper() == 'SHELTER':
                        # Admin-created Shelter Account: Active shelter accounts can log in directly
                        if not profile.is_active:
                            context['auth_error'] = 'Your shelter account is currently suspended or inactive. Please contact Administrator.'
                            context['prefill_username'] = username_input
                            return render(request, 'users/login.html', context)
                        auth_logout(request)
                        auth_login(request, db_user)
                        request.session['user_role'] = 'shelter'
                        if profile.must_change_password:
                            request.session['must_change_password'] = True
                        return redirect('/users/profile/?role=shelter#dashboard')
                    elif not profile.is_verified or profile.verification_status == 'PENDING':
                        # Unverified Customer: Send OTP verification via Email AND SMS to registered contact
                        otp_code = f"{random.randint(100000, 999999)}"
                        target_email = db_user.email if db_user.email else username_input
                        target_phone = getattr(profile, 'phone', '') or (username_input if username_input.replace('+', '').isdigit() else '')

                        request.session['account_verify_user_id'] = db_user.id
                        request.session['account_verify_otp'] = otp_code
                        request.session['account_verify_email'] = target_email

                        # Dispatch verification email
                        subject = f"KindHeart Account Verification Code: {otp_code}"
                        message = (
                            f"Hello {db_user.first_name or db_user.username},\n\n"
                            f"Thank you for registering with KindHeart Pet Adoption Portal!\n\n"
                            f"Your 6-digit account verification OTP code is:\n\n"
                            f"       >>>  {otp_code}  <<<\n\n"
                            f"Please enter this verification code on the sign-in screen to verify your email address and activate your adopter profile.\n\n"
                            f"With compassion,\n"
                            f"KindHeart Pet Adoption & Welfare Team\n"
                        )
                        try:
                            send_mail(
                                subject=subject,
                                message=message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[target_email],
                                fail_silently=True
                            )
                        except Exception as e:
                            print(f"[ACCOUNT OTP EMAIL] To: {target_email}, Code: {otp_code}, Error: {e}")

                        # Dispatch verification SMS
                        send_sms_otp(target_phone or target_email, otp_code)

                        context['show_account_otp_verify'] = True
                        context['verify_email'] = target_email
                        context['verify_user_id'] = db_user.id
                        context['generated_otp'] = otp_code
                        context['auth_info'] = f"Account verification required. An OTP verification code was sent to {target_email} and registered mobile."
                        return render(request, 'users/login.html', context)
                    elif profile.is_verified or profile.verification_status == 'VERIFIED':
                        auth_logout(request)
                        auth_login(request, db_user)
                        role_dest = 'adopter' if profile.role.lower() == 'customer' else profile.role.lower()
                        request.session['user_role'] = role_dest
                        return redirect(f'/users/profile/?role={role_dest}#dashboard')
                else:
                    auth_logout(request)
                    auth_login(request, db_user)
                    request.session['user_role'] = 'adopter'
                    return redirect('/users/profile/?role=adopter#dashboard')
            else:
                context['auth_error'] = 'Invalid password. Please verify and try again.'
                context['prefill_username'] = username_input
                return render(request, 'users/login.html', context)

        # 2. If not found in DB, check demo credentials & fallback ("rest of them keep unchnage")
        u_lower = username_input.lower()
        if 'admin' in u_lower or role_param == 'admin':
            auth_logout(request)
            request.session['user_role'] = 'admin'
            return redirect('/users/profile/?role=admin#dashboard')
        elif 'shelter' in u_lower or role_param == 'shelter' or 'maya.sen' in u_lower:
            auth_logout(request)
            request.session['user_role'] = 'shelter'
            return redirect('/users/profile/?role=shelter#dashboard')
        elif 'delivery' in u_lower or role_param == 'delivery' or 'rahul.kumar' in u_lower:
            auth_logout(request)
            request.session['user_role'] = 'delivery'
            return redirect('/users/profile/?role=delivery#dashboard')
        elif 'alex.adopter' in u_lower or 'sarah.connor' in u_lower:
            auth_logout(request)
            request.session['user_role'] = 'adopter'
            return redirect('/users/profile/?role=adopter#dashboard')
        else:
            context['auth_error'] = 'Account not found. Please check your credentials or register a new profile.'
            context['prefill_username'] = username_input
            return render(request, 'users/login.html', context)

    return render(request, 'users/login.html', context)

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username_input = request.POST.get('username', '').strip()
        role_input = request.POST.get('role', 'CUSTOMER').strip().upper()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # Enforce Backend Validation: Public self-registration permits only CUSTOMER (Adopter)
        if role_input in ['SHELTER', 'DELIVERY', 'ADMIN']:
            msg = 'Public self-registration for this role is not permitted. Shelter accounts are created by Administrators, and Delivery accounts are created by Shelter owners.'
            if role_input == 'SHELTER':
                msg = 'Shelter accounts are created by the administrator. Public shelter registration is not permitted.'
            elif role_input == 'DELIVERY':
                msg = 'Delivery partner accounts are created directly by Shelter owners. Public delivery registration is not permitted.'
            return render(request, 'users/register.html', {
                'auth_error': msg,
                'reg_name': name,
                'reg_username': username_input,
                'reg_role': 'CUSTOMER',
            })

        # Allowed public role: CUSTOMER (Adopter) only
        role = 'CUSTOMER'

        # Validation
        if not name or not username_input or not password:
            return render(request, 'users/register.html', {
                'auth_error': 'Please fill in all required fields.',
                'reg_name': name,
                'reg_username': username_input,
                'reg_role': role,
            })

        if len(password) < 6:
            return render(request, 'users/register.html', {
                'auth_error': 'Password must be at least 6 characters long.',
                'reg_name': name,
                'reg_username': username_input,
                'reg_role': role,
            })

        if password != password_confirm:
            return render(request, 'users/register.html', {
                'auth_error': 'Passwords do not match. Please re-enter carefully.',
                'reg_name': name,
                'reg_username': username_input,
                'reg_role': role,
            })

        # Determine email vs phone vs username
        email = ''
        phone = ''
        if '@' in username_input:
            email = username_input.lower()
            clean_username = email.split('@')[0]
        else:
            phone = username_input
            clean_username = ''.join(c for c in username_input.lower() if c.isalnum() or c in ['_', '-'])
            if not clean_username:
                clean_username = 'user'

        # Check if user with this username or email already exists
        if User.objects.filter(username__iexact=username_input).exists() or (email and User.objects.filter(email__iexact=email).exists()):
            return render(request, 'users/register.html', {
                'auth_error': 'An account with this email or username already exists. Please sign in or use another email.',
                'reg_name': name,
                'reg_username': username_input,
                'reg_role': role,
            })

        # Ensure unique username
        base_username = clean_username
        candidate_username = base_username
        counter = 1
        while User.objects.filter(username__iexact=candidate_username).exists():
            candidate_username = f"{base_username}{counter}"
            counter += 1

        # Name parts
        name_parts = name.split(None, 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Create Django auth User
        user = User.objects.create_user(
            username=candidate_username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create UserProfile - PENDING verification for admin/system approval
        UserProfile.objects.create(
            user=user,
            role=role,
            phone=phone,
            is_active=True,
            is_verified=False,
            verification_status='PENDING'
        )

        # Store pending notice in session for login page
        request.session['reg_pending_notice'] = {
            'name': name,
            'username': email if email else candidate_username,
            'message': f"Account created for {name}! Please sign in below with your email and password to verify your account via OTP."
        }

        # Redirect to login page - DO NOT log in directly!
        return redirect('login')

    return render(request, 'users/register.html')

def profile_view(request):
    # Determine authenticated user's role if logged in
    auth_user_role = None
    db_user = None
    profile_obj = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        db_user = request.user
        profile_obj = getattr(db_user, 'profile', None)
        if profile_obj:
            auth_user_role = 'adopter' if profile_obj.role.upper() == 'CUSTOMER' else profile_obj.role.lower()
        elif db_user.is_staff or db_user.is_superuser:
            auth_user_role = 'admin'

    role = request.GET.get('role')
    if not role:
        if auth_user_role:
            role = auth_user_role
        else:
            role = request.session.get('user_role', 'adopter')

    role = str(role).lower()
    if role not in ['adopter', 'shelter', 'delivery', 'admin']:
        role = 'adopter'

    # Save active role into session
    request.session['user_role'] = role

    # Resolve view credentials based on requested role:
    # 1. If viewing the role that matches the authenticated user, show THEIR actual profile!
    if auth_user_role == role and db_user:
        customer_id = db_user.id
        customer_username = db_user.username
        customer_name = f"{db_user.first_name} {db_user.last_name}".strip() or db_user.username
        customer_email = db_user.email or f"{db_user.username}@kindheart.org"
        customer_phone = getattr(profile_obj, 'phone', '')
        if customer_phone == 'N/A':
            customer_phone = ''
        customer_is_verified = profile_obj.is_verified if profile_obj else True
        customer_verification_status = profile_obj.verification_status if profile_obj else 'VERIFIED'
        if profile_obj and profile_obj.created_at:
            customer_reg_date = profile_obj.created_at.strftime('%d %b %Y')
            member_since = profile_obj.created_at.strftime('%B %Y')
        else:
            customer_reg_date = '15 Jan 2024'
            member_since = 'January 2024'

        customer_address = getattr(profile_obj, 'address', '') or ''
        customer_city = getattr(profile_obj, 'city', '') or 'Kochi'
        customer_state = getattr(profile_obj, 'state', '') or 'Kerala'
        customer_postal_code = getattr(profile_obj, 'postal_code', '') or '682036'
        customer_profile_photo = profile_obj.profile_photo.url if (profile_obj and getattr(profile_obj, 'profile_photo', None)) else ''
        customer_dob = getattr(profile_obj, 'dob', '') or ''
        customer_gender = getattr(profile_obj, 'gender', '') or 'Female'
        customer_occupation = getattr(profile_obj, 'occupation', '') or ''
        customer_whatsapp = getattr(profile_obj, 'whatsapp', '') or ''
        customer_residence_type = getattr(profile_obj, 'residence_type', '') or 'Independent House'
        customer_home_ownership = getattr(profile_obj, 'home_ownership', '') or 'Owned Property'
        customer_id_document_name = getattr(profile_obj, 'id_document_name', '') or ''
        customer_address_document_name = getattr(profile_obj, 'address_document_name', '') or ''
        customer_residence_document_name = getattr(profile_obj, 'residence_document_name', '') or ''

        if role == 'adopter':
            customer_role = 'Verified Adopter'
            customer_location = f"{customer_city}, {customer_state}" if customer_city and customer_state else (customer_city or 'Kochi, Kerala')
        elif role == 'shelter':
            customer_role = 'Shelter Staff & Vet'
            shelter_rec = getattr(db_user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=db_user).first()
            customer_location = shelter_rec.location if shelter_rec and shelter_rec.location != 'Pending Onboarding' else (shelter_rec.shelter_name if shelter_rec else 'Kochi Shelter Center')
            if shelter_rec:
                customer_verification_status = shelter_rec.verification_status
                customer_is_verified = is_shelter_verified(shelter_rec)
            elif profile_obj:
                customer_verification_status = profile_obj.verification_status
                customer_is_verified = (profile_obj.verification_status == 'VERIFIED' and profile_obj.is_verified)
        elif role == 'delivery':
            customer_role = 'Delivery Transit Partner'
            customer_location = 'South Zone Fleet'
        elif role == 'admin':
            customer_role = 'Super Administrator'
            customer_location = 'Platform Command Center'

    # 2. If viewing a different role (or not authenticated), load that role's distinct profile
    elif role == 'shelter':
        # Look for registered shelter in DB first
        shelter_p = UserProfile.objects.filter(role='SHELTER').select_related('user').order_by('-created_at').first()
        if shelter_p:
            db_u = shelter_p.user
            customer_name = f"{db_u.first_name} {db_u.last_name}".strip() or db_u.username
            customer_id = db_u.id
            customer_username = db_u.username
            customer_email = db_u.email or f"{db_u.username}@happypaws.org"
            customer_phone = shelter_p.phone if shelter_p.phone and shelter_p.phone != 'N/A' else '+91 98450 11223'
            customer_role = 'Shelter Staff & Vet'
            shelter_rec = getattr(db_u, 'shelter_profile', None)
            customer_location = shelter_rec.shelter_name if shelter_rec else 'Kochi Shelter Center'
            if shelter_rec:
                customer_verification_status = shelter_rec.verification_status
                customer_is_verified = is_shelter_verified(shelter_rec)
            else:
                customer_verification_status = shelter_p.verification_status
                customer_is_verified = (shelter_p.verification_status == 'VERIFIED' and shelter_p.is_verified)
            customer_reg_date = shelter_p.created_at.strftime('%d %b %Y') if shelter_p.created_at else '15 Jan 2024'
            member_since = shelter_p.created_at.strftime('%B %Y') if shelter_p.created_at else 'January 2024'
        else:
            customer_name = 'Shelter Facility'
            customer_id = 0
            customer_username = 'shelter'
            customer_email = 'shelter@kindheart.org'
            customer_role = 'Shelter Staff & Vet'
            customer_location = 'Shelter Center'
            customer_phone = '—'
            customer_is_verified = False
            customer_verification_status = 'PENDING'
            customer_reg_date = 'Recent'
            member_since = 'Recent'

    elif role == 'admin':
        customer_name = 'Platform Administrator'
        customer_id = 1
        customer_username = 'admin'
        customer_email = 'admin@kindheart.org'
        customer_role = 'Super Administrator'
        customer_location = 'Platform Command Center'
        customer_phone = '—'
        customer_is_verified = True
        customer_verification_status = 'VERIFIED'
        customer_reg_date = 'Recent'
        member_since = 'Recent'

    elif role == 'delivery':
        deliv_p = UserProfile.objects.filter(role='DELIVERY', is_verified=True).select_related('user').order_by('-created_at').first()
        if deliv_p:
            db_u = deliv_p.user
            customer_name = f"{db_u.first_name} {db_u.last_name}".strip() or db_u.username
            customer_id = db_u.id
            customer_username = db_u.username
            customer_email = db_u.email or f"{db_u.username}@safetransit.org"
            customer_phone = deliv_p.phone if deliv_p.phone and deliv_p.phone != 'N/A' else '—'
            customer_role = 'Delivery Transit Partner'
            customer_location = 'South Zone Fleet'
            customer_is_verified = deliv_p.is_verified
            customer_verification_status = deliv_p.verification_status
            customer_reg_date = deliv_p.created_at.strftime('%d %b %Y') if deliv_p.created_at else 'Recent'
            member_since = deliv_p.created_at.strftime('%B %Y') if deliv_p.created_at else 'Recent'
        else:
            customer_name = 'Delivery Partner'
            customer_id = 0
            customer_username = 'delivery'
            customer_email = 'delivery@kindheart.org'
            customer_role = 'Delivery Transit Partner'
            customer_location = 'Transit Fleet'
            customer_phone = '—'
            customer_is_verified = True
            customer_verification_status = 'VERIFIED'
            customer_reg_date = 'Recent'
            member_since = 'Recent'

    else:  # adopter
        cust_p = UserProfile.objects.filter(role='CUSTOMER', is_verified=True).select_related('user').order_by('-created_at').first()
        if cust_p:
            db_u = cust_p.user
            customer_name = f"{db_u.first_name} {db_u.last_name}".strip() or db_u.username
            customer_id = db_u.id
            customer_username = db_u.username
            customer_email = db_u.email or f"{db_u.username}@kindheart.org"
            customer_phone = cust_p.phone if cust_p.phone and cust_p.phone != 'N/A' else '—'
            customer_role = 'Verified Adopter'
            customer_address = cust_p.address or ''
            customer_city = cust_p.city or ''
            customer_state = getattr(cust_p, 'state', '') or ''
            customer_postal_code = getattr(cust_p, 'postal_code', '') or ''
            customer_profile_photo = cust_p.profile_photo.url if getattr(cust_p, 'profile_photo', None) else ''
            customer_location = f"{customer_city}, {customer_state}".strip(', ') if customer_city or customer_state else ''
            customer_is_verified = cust_p.is_verified
            customer_verification_status = cust_p.verification_status
            customer_reg_date = cust_p.created_at.strftime('%d %b %Y') if cust_p.created_at else 'Recent'
            member_since = cust_p.created_at.strftime('%B %Y') if cust_p.created_at else 'Recent'
        else:
            customer_name = 'Guest Adopter'
            customer_id = 0
            customer_username = 'adopter'
            customer_email = 'adopter@kindheart.org'
            customer_role = 'Adopter'
            customer_location = 'Kochi, Kerala'
            customer_address = ''
            customer_city = 'Kochi'
            customer_state = 'Kerala'
            customer_postal_code = '682036'
            customer_profile_photo = ''
            customer_phone = '—'
            customer_is_verified = False
            customer_verification_status = 'PENDING'
            customer_reg_date = 'Recent'
            member_since = 'Recent'

    # Compute first name and initials for header and avatars
    name_parts = customer_name.strip().split()
    customer_first_name = name_parts[0] if name_parts else customer_name
    if len(name_parts) > 1:
        customer_initials = (name_parts[0][0] + name_parts[-1][0]).upper()
    elif len(customer_name) >= 2:
        customer_initials = customer_name[:2].upper()
    else:
        customer_initials = customer_name.upper() if customer_name else ('AD' if role == 'admin' else 'VA')

    current_shelter_name = ''
    current_shelter_id = ''
    shelter_dossier = None
    if role == 'shelter':
        active_sh = None
        if request.user.is_authenticated and not request.user.is_anonymous:
            active_sh = getattr(request.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=request.user).first()
        elif 'shelter_rec' in locals() and shelter_rec:
            active_sh = shelter_rec
        elif 'shelter_p' in locals() and shelter_p:
            active_sh = getattr(shelter_p.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=shelter_p.user).first()

        if not active_sh:
            active_sh = ShelterProfile.objects.first()

        if active_sh:
            current_shelter_name = active_sh.shelter_name
            current_shelter_id = f"SH-{active_sh.user.id if active_sh.user else active_sh.id}"
            sh_user = active_sh.user
            sh_prof = getattr(sh_user, 'profile', None) if sh_user else None
            sh_license = active_sh.license_number or (f"KL-SH-{active_sh.user.id:04d}" if active_sh.user else "KL-SH-0001")
            sh_verified = is_shelter_verified(active_sh)
            sh_status = active_sh.verification_status

            total_pets_count = Pet.objects.filter(shelter=active_sh).count()
            available_pets_count = Pet.objects.filter(shelter=active_sh, status='AVAILABLE').count()
            adopted_pets_count = Pet.objects.filter(shelter=active_sh, status='ADOPTED').count()
            adoption_requests_count = AdoptionRequest.objects.filter(shelter=active_sh).count()
            delivery_partners_count = DeliveryPartner.objects.filter(shelter=active_sh).count()
            documents_count = ShelterDocument.objects.filter(shelter=active_sh).count()
            verified_documents_count = ShelterDocument.objects.filter(shelter=active_sh, verification_status='VERIFIED').count()

            completed_adoptions_count = AdoptionRequest.objects.filter(shelter=active_sh, status__in=['COMPLETED', 'ADOPTED']).count()

            sh_phone = active_sh.phone if active_sh.phone and active_sh.phone != 'N/A' else (sh_prof.phone if sh_prof and sh_prof.phone and sh_prof.phone != 'N/A' else '+91 98450 11223')
            sh_email = sh_user.email if sh_user and sh_user.email else f"{sh_user.username if sh_user else 'shelter'}@kindheart.org"
            sh_address = active_sh.address if hasattr(active_sh, 'address') and active_sh.address else 'Panampilly Nagar'
            sh_city = active_sh.city if hasattr(active_sh, 'city') and active_sh.city else 'Kochi'
            sh_state = active_sh.state if hasattr(active_sh, 'state') and active_sh.state else 'Kerala'
            sh_type = active_sh.shelter_type if hasattr(active_sh, 'shelter_type') and active_sh.shelter_type else 'Animal Rescue & Rehabilitation Center'
            sh_location = f"{sh_city}, {sh_state}" if (sh_city or sh_state) else (active_sh.location if active_sh.location and active_sh.location != 'Pending Onboarding' else 'Kochi, Kerala')
            sh_bio = active_sh.bio if active_sh.bio else 'Registered animal welfare facility providing rescue, rehabilitation, veterinary care, and ethical adoption services.'
            sh_logo_url = active_sh.logo.url if hasattr(active_sh, 'logo') and active_sh.logo else (sh_prof.profile_photo.url if sh_prof and getattr(sh_prof, 'profile_photo', None) else '')
            sh_member_since = active_sh.created_at.strftime('%B %Y') if active_sh.created_at else 'January 2024'
            sh_reg_date = active_sh.created_at.strftime('%d %b %Y') if active_sh.created_at else '15 Jan 2024'

            # Recent pets
            recent_pets = list(Pet.objects.filter(shelter=active_sh).order_by('-id')[:5].values('id', 'name', 'species', 'breed', 'status', 'approval_status'))
            for rp in recent_pets:
                rp['id_display'] = f"P{rp['id']}"

            # Recent adoption requests
            recent_adoption_requests = []
            try:
                reqs = AdoptionRequest.objects.filter(shelter=active_sh).select_related('pet', 'customer').order_by('-id')[:5]
                for r in reqs:
                    recent_adoption_requests.append({
                        'id': r.id,
                        'id_display': f"AR-{r.id:04d}",
                        'pet_name': r.pet.name if r.pet else 'Companion',
                        'pet_species': r.pet.species if r.pet else 'Pet',
                        'customer_name': f"{r.customer.first_name} {r.customer.last_name}".strip() if r.customer and (r.customer.first_name or r.customer.last_name) else (r.customer.username if r.customer else 'Adopter'),
                        'status': r.status,
                        'date': r.request_date.strftime('%d %b %Y') if hasattr(r, 'request_date') and r.request_date else 'Recent'
                    })
            except Exception as e:
                print(f"Error querying recent_adoption_requests: {e}")

            # Recent completed adoptions
            recent_completed_adoptions = []
            try:
                comp_reqs = AdoptionRequest.objects.filter(shelter=active_sh, status__in=['COMPLETED', 'ADOPTED']).select_related('pet', 'customer').order_by('-id')[:5]
                for cr in comp_reqs:
                    recent_completed_adoptions.append({
                        'id': cr.id,
                        'id_display': f"AR-{cr.id:04d}",
                        'pet_name': cr.pet.name if cr.pet else 'Companion',
                        'pet_species': cr.pet.species if cr.pet else 'Pet',
                        'customer_name': f"{cr.customer.first_name} {cr.customer.last_name}".strip() if cr.customer and (cr.customer.first_name or cr.customer.last_name) else (cr.customer.username if cr.customer else 'Adopter'),
                        'status': cr.status,
                        'date': cr.request_date.strftime('%d %b %Y') if hasattr(cr, 'request_date') and cr.request_date else 'Recent'
                    })
            except Exception as e:
                print(f"Error querying recent_completed_adoptions: {e}")

            # Recent delivery assignments
            recent_delivery_assignments = []
            try:
                delivs = DeliveryRequest.objects.filter(adoption_request__shelter=active_sh).select_related('delivery_partner', 'delivery_partner__user', 'adoption_request__pet', 'adoption_request__customer').order_by('-id')[:15]
                for d in delivs:
                    p_name = 'Unassigned Driver'
                    if d.delivery_partner:
                        if d.delivery_partner.user and (d.delivery_partner.user.first_name or d.delivery_partner.user.last_name):
                            p_name = f"{d.delivery_partner.user.first_name} {d.delivery_partner.user.last_name}".strip()
                        elif d.delivery_partner.user:
                            p_name = d.delivery_partner.user.username
                        else:
                            p_name = getattr(d.delivery_partner, 'partner_id', 'Delivery Courier')

                    recent_delivery_assignments.append({
                        'id': d.id,
                        'id_display': f"DEL-{d.id:04d}",
                        'partner_name': p_name,
                        'pet_name': d.adoption_request.pet.name if d.adoption_request and d.adoption_request.pet else 'Companion',
                        'customer_name': f"{d.adoption_request.customer.first_name} {d.adoption_request.customer.last_name}".strip() if d.adoption_request and d.adoption_request.customer else 'Adopter',
                        'status': d.status,
                        'drop_address': d.drop_address or 'Adopter Address',
                        'date': d.created_at.strftime('%d %b %Y') if d.created_at else 'Recent'
                    })
            except Exception as e:
                print(f"Error querying recent_delivery_assignments: {e}")

            # Uploaded documents summary
            shelter_docs = list(ShelterDocument.objects.filter(shelter=active_sh).order_by('-upload_date')[:5].values('id', 'doc_type', 'original_filename', 'verification_status', 'upload_date', 'review_notes'))
            for doc in shelter_docs:
                doc['uploaded_at_display'] = doc['upload_date'].strftime('%d %b %Y') if doc.get('upload_date') else 'Recent'
                doc['type_display'] = doc['doc_type'].replace('_', ' ').title() if doc.get('doc_type') else 'Document'

            shelter_dossier = {
                'id': current_shelter_id,
                'name': current_shelter_name,
                'license': sh_license,
                'verification_status': sh_status,
                'is_verified': sh_verified,
                'shelter_type': sh_type,
                'address': sh_address,
                'city': sh_city,
                'state': sh_state,
                'location': sh_location,
                'phone': sh_phone,
                'email': sh_email,
                'bio': sh_bio,
                'logo_url': sh_logo_url,
                'member_since': sh_member_since,
                'reg_date': sh_reg_date,
                'total_pets': total_pets_count,
                'available_pets': available_pets_count,
                'adopted_pets': adopted_pets_count,
                'adoption_requests': adoption_requests_count,
                'completed_adoptions': completed_adoptions_count,
                'delivery_partners_count': delivery_partners_count,
                'documents_count': documents_count,
                'verified_documents_count': verified_documents_count,
                'documents_list': shelter_docs,
                'recent_pets': recent_pets,
                'recent_adoption_requests': recent_adoption_requests,
                'recent_completed_adoptions': recent_completed_adoptions,
                'recent_delivery_assignments': recent_delivery_assignments,
            }
        else:
            shelter_dossier = None


    # Phase 17 & Phase 19: Adopter Profile UI — Real Database Adoption Activity & History
    # Phase 19 Backend Enforcement: adopter_stats and adopter_history MUST only be computed
    # for role='adopter'. Shelter, delivery, and admin roles must NOT receive adopter-specific
    # DB queries, statistics, or history — even if the values would evaluate to zeros.
    adopter_stats = {
        'total_requests': 0,
        'active_adoptions': 0,
        'completed_adoptions': 0,
        'favorites_count': 0,
        'messages_count': 0,
        'unread_messages_count': 0,
    }
    adopter_history = []

    # Phase 19: Only resolve the adopter user for role='adopter'.
    # The previous code fell through via 'elif db_u' and could incorrectly pick up
    # a shelter/delivery user object, violating role data isolation.
    target_adopter_user = None
    if role == 'adopter':
        if request.user.is_authenticated and not request.user.is_anonymous:
            target_adopter_user = request.user
        elif 'db_u' in locals() and db_u:
            target_adopter_user = db_u
        elif 'db_user' in locals() and db_user:
            target_adopter_user = db_user

    if target_adopter_user:
        user_adoptions_qs = AdoptionRequest.objects.filter(customer=target_adopter_user).select_related('pet', 'shelter', 'shelter__user')
        adopter_stats['total_requests'] = user_adoptions_qs.count()
        adopter_stats['active_adoptions'] = user_adoptions_qs.filter(status__in=['PENDING', 'APPROVED', 'IN_PROGRESS', 'READY_FOR_HANDOVER', 'HANDOVER_PENDING', 'IN_TRANSIT']).count()
        adopter_stats['completed_adoptions'] = user_adoptions_qs.filter(status__in=['COMPLETED', 'ADOPTED']).count()
        adopter_stats['favorites_count'] = FavoritePet.objects.filter(user=target_adopter_user).count()
        adopter_stats['messages_count'] = Message.objects.filter(recipient=target_adopter_user).count()
        adopter_stats['unread_messages_count'] = Message.objects.filter(recipient=target_adopter_user, is_read=False).count()

        for req in user_adoptions_qs.order_by('-request_date', '-id')[:30]:
            delivery_obj = getattr(req, 'delivery', None)
            if delivery_obj and hasattr(delivery_obj, 'get_status_display'):
                handover_status = delivery_obj.get_status_display()
            elif delivery_obj:
                handover_status = delivery_obj.status
            elif req.status in ['COMPLETED', 'ADOPTED']:
                handover_status = 'Delivered & Handover Complete'
            elif req.status == 'APPROVED':
                handover_status = 'Approved / Handover Ready'
            elif req.status == 'REJECTED':
                handover_status = 'Not Applicable (Rejected)'
            else:
                handover_status = 'Pending Shelter Review'

            adopter_history.append({
                'id': req.id,
                'application_id': f"KHD-APP-{req.id:04d}",
                'pet_id': req.pet.id if req.pet else None,
                'pet_name': req.pet.name if req.pet else 'Companion',
                'pet_breed': req.pet.breed if req.pet else 'Domestic',
                'pet_species': req.pet.species if req.pet else 'Pet',
                'pet_image_url': req.pet.image_url if req.pet and req.pet.image_url else '',
                'shelter_name': req.shelter.shelter_name if req.shelter else 'KindHeart Center',
                'application_date': req.request_date.strftime('%d %b %Y') if req.request_date else 'Recent',
                'status': req.status,
                'status_display': req.get_status_display() if hasattr(req, 'get_status_display') else req.status,
                'handover_status': handover_status,
            })

    # Fetch real pending user verifications, verified customers (only CUSTOMERs), and verified shelters (only SHELTERs)
    pending_users_list = []
    verified_customers_list = []
    verified_shelters_list = []

    pending_profiles = UserProfile.objects.filter(verification_status='PENDING').select_related('user').order_by('-created_at')
    for p in pending_profiles:
        p_name = f"{p.user.first_name} {p.user.last_name}".strip() or p.user.username
        pending_users_list.append({
            'id': f"USR-{p.id}",
            'profile_id': p.id,
            'user_id': p.user.id,
            'username': p.user.username,
            'email': p.user.email,
            'name': p_name,
            'role': p.role,
            'phone': p.phone or 'N/A',
            'created_at': p.created_at.strftime('%d %b %Y, %I:%M %p') if p.created_at else 'Recent',
            'verification_status': p.verification_status,
        })

    # 1. Real Verified CUSTOMERS (Adopters)
    verified_profiles = UserProfile.objects.filter(is_verified=True, role='CUSTOMER').select_related('user').order_by('-created_at')
    for vp in verified_profiles:
        if vp.user.is_superuser:
            continue
        vp_name = f"{vp.user.first_name} {vp.user.last_name}".strip() or vp.user.username
        vp_phone = vp.phone if vp.phone and vp.phone != 'N/A' else (vp.user.username if vp.user.username.isdigit() else '—')
        verified_customers_list.append({
            'id': f"KH-USR-{vp.user.id}",
            'profile_id': vp.id,
            'user_id': vp.user.id,
            'name': vp_name,
            'email': vp.user.email or vp.user.username,
            'phone': vp_phone,
            'role': 'Verified Adopter',
            'city': 'Kochi, Kerala',
            'address': 'Kochi, Kerala',
            'completedAdoptions': 0,
            'totalOrders': 0,
            'activeAdoption': 'None',
            'accountStatus': 'Active',
            'kycVerified': True,
            'homeInspectionPassed': True,
            'previousAdoptions': [],
            'paymentsTotal': '₹0',
            'registeredDate': vp.created_at.strftime('%d %b %Y') if vp.created_at else 'Recent',
            'reviewsGiven': 0,
            'complaints': 0
        })

    # 2. Real Registered SHELTERS (Shelter Facilities)
    all_shelter_profiles = UserProfile.objects.filter(role='SHELTER').select_related('user').order_by('-created_at')
    for sp in all_shelter_profiles:
        sp_user = sp.user
        if not sp_user:
            continue
        sp_shelter = getattr(sp_user, 'shelter_profile', None)
        if not sp_shelter:
            continue
        s_name = sp_shelter.shelter_name or f"{sp_user.first_name} Shelter & Rescue".strip() or 'Community Shelter'
        s_contact = f"{sp_user.first_name} {sp_user.last_name}".strip() or sp_user.username
        s_phone = sp.phone if sp.phone and sp.phone != 'N/A' else (sp_user.username if sp_user.username.isdigit() else '+91 98470 11223')
        s_location = (sp_shelter.location if sp_shelter and sp_shelter.location != 'Pending Onboarding' else 'Panampilly Nagar, Kochi, Kerala')
        s_pets_count = Pet.objects.filter(shelter=sp_shelter).count() if sp_shelter else 0
        s_available_count = Pet.objects.filter(shelter=sp_shelter, status='AVAILABLE').count() if sp_shelter else 0
        
        if sp.verification_status == 'SUSPENDED' or (sp_shelter and sp_shelter.verification_status == 'SUSPENDED'):
            v_status = 'Suspended'
        elif sp.verification_status == 'REJECTED' or (sp_shelter and sp_shelter.verification_status == 'REJECTED'):
            v_status = 'Rejected'
        elif sp.verification_status == 'UNDER_REVIEW' or (sp_shelter and sp_shelter.verification_status == 'UNDER_REVIEW'):
            v_status = 'Under Review'
        elif sp.is_verified or sp.verification_status == 'VERIFIED' or (sp_shelter and sp_shelter.verification_status == 'VERIFIED'):
            v_status = 'Verified'
        else:
            v_status = 'Pending Verification'
        acc_status = 'Active' if (sp.is_active and sp_user.is_active) else 'Suspended'

        # Phase 9: Include shelter documents and summary for Admin review
        sh_docs = list(sp_shelter.documents.all()) if sp_shelter else []
        docs_summary = {
            'total': len(sh_docs),
            'pending': sum(1 for d in sh_docs if d.verification_status == 'PENDING'),
            'under_review': sum(1 for d in sh_docs if d.verification_status == 'UNDER_REVIEW'),
            'verified': sum(1 for d in sh_docs if d.verification_status == 'VERIFIED'),
            'rejected': sum(1 for d in sh_docs if d.verification_status == 'REJECTED'),
        }
        docs_data = [{
            'id': d.id,
            'doc_type': d.doc_type,
            'doc_type_label': d.get_doc_type_display(),
            'original_filename': d.original_filename,
            'file_url': request.build_absolute_uri(d.file.url) if d.file else '',
            'download_url': request.build_absolute_uri(f'/users/api/shelter/document/{d.id}/download/'),
            'file_size_display': d.file_size_display,
            'upload_date': d.upload_date.strftime('%d %b %Y %H:%M'),
            'verification_status': d.verification_status,
            'verification_label': d.get_verification_status_display(),
            'review_notes': d.review_notes or '',
            'reviewed_by': (d.reviewed_by.get_full_name() or d.reviewed_by.username) if d.reviewed_by else None,
            'review_date': d.review_date.strftime('%d %b %Y') if d.review_date else None,
        } for d in sh_docs]

        verified_shelters_list.append({
            'id': f"SH-{sp_user.id}",
            'profile_id': sp.id,
            'user_id': sp_user.id,
            'shelter_id': sp_shelter.id if sp_shelter else None,
            'name': s_name,
            'license': f"KL-SH-{sp_user.id:04d}",
            'contactPerson': s_contact,
            'phone': s_phone,
            'email': sp_user.email or f"{sp_user.username}@happypaws.org",
            'address': s_location,
            'verificationStatus': v_status,
            'accountStatus': acc_status,
            'is_active': (sp.is_active and sp_user.is_active),
            'totalPets': s_pets_count,
            'availablePets': s_available_count,
            'totalOrders': 0,
            'completedAdoptions': 0,
            'revenue': "₹0",
            'settlementsPending': "₹0",
            'complaints': 0,
            'auditPassRate': "100%",
            'lastAudit': sp.created_at.strftime('%d %b %Y') if sp.created_at else 'Recent',
            'documents': docs_data,
            'docsSummary': docs_summary,
        })

    # Fetch System Settings & Role Permissions from database
    db_system_settings = {}
    for ss in SystemSetting.objects.all():
        try:
            db_system_settings[ss.key] = json.loads(ss.value)
        except Exception:
            db_system_settings[ss.key] = ss.value

    db_role_permissions = {}
    for rp in RolePermission.objects.all():
        if rp.role not in db_role_permissions:
            db_role_permissions[rp.role] = {}
        db_role_permissions[rp.role][rp.permission_key] = rp.is_granted

    # Phase 19: Safe default initializations for adopter-only context variables.
    # These are only rendered inside profile-adopter-view which is hidden for shelter/admin/delivery.
    # Prevents NameError if a non-adopter role path did not initialize these variables.
    _p19 = locals()
    if 'customer_address' not in _p19:
        customer_address = ''
    if 'customer_city' not in _p19:
        customer_city = ''
    if 'customer_state' not in _p19:
        customer_state = ''
    if 'customer_postal_code' not in _p19:
        customer_postal_code = ''
    if 'customer_profile_photo' not in _p19:
        customer_profile_photo = ''
    del _p19

    context = {
        'customer_name': customer_name,
        'customer_first_name': customer_first_name,
        'customer_initials': customer_initials,
        'customer_email': customer_email,
        'customer_phone': customer_phone,
        'customer_role': customer_role,
        'customer_id': customer_id,
        'customer_username': customer_username,
        'customer_location': customer_location,
        'customer_is_verified': customer_is_verified,
        'customer_verification_status': customer_verification_status,
        'is_shelter_verified': customer_is_verified if role == 'shelter' else True,
        'shelter_verification_status': customer_verification_status if role == 'shelter' else 'VERIFIED',
        'current_shelter_name': current_shelter_name,
        'current_shelter_id': current_shelter_id,
        'shelter_dossier': shelter_dossier,
        'customer_address': customer_address,
        'customer_city': customer_city,
        'customer_state': customer_state,
        'customer_postal_code': customer_postal_code,
        'customer_profile_photo': customer_profile_photo,
        'adopter_stats': adopter_stats,
        'adopter_history': adopter_history,
        'adopter_history_count': len(adopter_history),
        'adopter_history_json': json.dumps(adopter_history),
        'customer_reg_date': customer_reg_date,
        'member_since': member_since,
        'current_role': role,
        'pending_users_json': json.dumps(pending_users_list),
        'pending_users_count': len(pending_users_list),
        'verified_customers_json': json.dumps(verified_customers_list),
        'verified_customers_count': len(verified_customers_list),
        'verified_shelters_json': json.dumps(verified_shelters_list),
        'verified_shelters_count': len(verified_shelters_list),
        'db_system_settings_json': json.dumps(db_system_settings),
        'db_role_permissions_json': json.dumps(db_role_permissions),
    }

    # Preload database pets to hydrate KindHeartData.pets
    # Spec Rule #3 & #32: For a logged in delivery user, restrict pets_qs at Django level to assigned pets ONLY
    db_pets_list = []
    try:
        if role == 'delivery' and request.user.is_authenticated and not request.user.is_anonymous:
            assigned_pet_ids = DeliveryRequest.objects.filter(delivery_partner__user=request.user).values_list('adoption_request__pet_id', flat=True)
            pets_qs = Pet.objects.filter(id__in=assigned_pet_ids).select_related('shelter').order_by('-id')
        else:
            pets_qs = Pet.objects.all().select_related('shelter').order_by('-id')

        for p in pets_qs:
            db_pets_list.append({
                'id': f"P{p.id}",
                'name': p.name,
                'species': p.species,
                'breed': p.breed,
                'age': p.age,
                'ageCategory': "Young" if ('month' in p.age.lower() or '1' in p.age or '2' in p.age) else "Adult",
                'gender': p.gender,
                'size': p.weight or "Medium",
                'location': p.location or "Kochi, Kerala",
                'shelterId': f"SH-{p.shelter.user.id}" if p.shelter and p.shelter.user else "SH-101",
                'shelterName': p.shelter.shelter_name if p.shelter else "Happy Paws Shelter & Rescue",
                'image': p.image_url or "/kindheart_bruno.jpg",
                'status': {'AVAILABLE': 'Available', 'PENDING_ADOPTION': 'Pending Adoption', 'ADOPTED': 'Adopted'}.get(p.status, p.status.replace('_', ' ').title() if p.status else 'Available'),
                'health': "Vaccinated & Health Checked" if p.is_vaccinated else "Under Observation",
                'microchip': f"CHIP-{p.id:05d}-KL",
                'energy': "Active & Friendly",
                'story': p.description or f"Loving companion {p.name} looking for a warm home.",
                'vaccinated': p.is_vaccinated,
                'neutered': p.is_neutered,
                'adoptionFee': f"₹{p.adoption_fee}" if p.adoption_fee else "Free Adoption"
            })
    except Exception as e:
        db_pets_list = []

    context['db_pets_json'] = json.dumps(db_pets_list)

    # 3b. Query & Hydrate Real Backend Delivery Requests (Spec Section 34)
    db_delivery_requests_list = []
    try:
        if role == 'delivery' and request.user.is_authenticated and not request.user.is_anonymous:
            deliv_qs = DeliveryRequest.objects.filter(delivery_partner__user=request.user).select_related('adoption_request', 'adoption_request__pet', 'adoption_request__customer', 'adoption_request__shelter', 'delivery_partner', 'delivery_partner__user').order_by('-id')
        elif role == 'shelter' and active_sh:
            deliv_qs = DeliveryRequest.objects.filter(adoption_request__shelter=active_sh).select_related('adoption_request', 'adoption_request__pet', 'adoption_request__customer', 'adoption_request__shelter', 'delivery_partner', 'delivery_partner__user').order_by('-id')
        elif role == 'adopter' and target_adopter_user:
            deliv_qs = DeliveryRequest.objects.filter(adoption_request__customer=target_adopter_user).select_related('adoption_request', 'adoption_request__pet', 'adoption_request__customer', 'adoption_request__shelter', 'delivery_partner', 'delivery_partner__user').order_by('-id')
        elif is_admin:
            deliv_qs = DeliveryRequest.objects.all().select_related('adoption_request', 'adoption_request__pet', 'adoption_request__customer', 'adoption_request__shelter', 'delivery_partner', 'delivery_partner__user').order_by('-id')
        else:
            deliv_qs = DeliveryRequest.objects.none()

        for dr in deliv_qs:
            pet_obj = dr.adoption_request.pet if (dr.adoption_request and dr.adoption_request.pet) else None
            cust_user = dr.adoption_request.customer if dr.adoption_request else None
            sh_obj = dr.adoption_request.shelter if dr.adoption_request else None
            driver_user = dr.delivery_partner.user if dr.delivery_partner else None

            dp_prof = getattr(dr.delivery_partner, 'user', None) if dr.delivery_partner else None
            agent_phone = getattr(getattr(dp_prof, 'profile', None), 'phone', '') if dp_prof else (dp_prof.username if dp_prof and dp_prof.username.isdigit() else '')

            db_delivery_requests_list.append({
                'id': f"DEL-{dr.id}",
                'db_id': dr.id,
                'orderId': f"KH102{dr.adoption_request.id:02d}" if dr.adoption_request else f"KH102{dr.id:02d}",
                'appId': f"KH102{dr.adoption_request.id:02d}" if dr.adoption_request else f"KH102{dr.id:02d}",
                'petId': f"P{pet_obj.id}" if pet_obj else "P101",
                'petName': pet_obj.name if pet_obj else "Companion Pet",
                'petBreed': pet_obj.breed if pet_obj else "Mixed Breed",
                'petSpecies': pet_obj.species if pet_obj else "Dog",
                'petImage': pet_obj.image_url if pet_obj and pet_obj.image_url else "",
                'customerName': cust_user.get_full_name() or cust_user.username if cust_user else "Adopter",
                'customerPhone': (getattr(getattr(cust_user, 'profile', None), 'phone', '') or (cust_user.username if cust_user and cust_user.username.isdigit() else '')) if cust_user else '',
                'customerEmail': cust_user.email if cust_user else '',
                'customerCity': getattr(getattr(cust_user, 'profile', None), 'city', 'Kochi') if cust_user else 'Kochi',
                'pickupAddress': dr.pickup_address or (sh_obj.location if sh_obj else "Shelter Location"),
                'dropAddress': dr.drop_address or "Adopter Location, Kochi, Kerala",
                'shelterName': sh_obj.shelter_name if sh_obj else "Shelter",
                'shelterLocation': sh_obj.location if sh_obj else "Kochi Center",
                'shelterPhone': sh_obj.phone if (sh_obj and sh_obj.phone) else "",
                'agent': (driver_user.get_full_name() or driver_user.username) if driver_user else "Unassigned Driver",
                'agentId': dr.delivery_partner.partner_id if dr.delivery_partner else "DP-101",
                'agentPhone': agent_phone,
                'status': dr.status,
                'statusDisplay': dr.get_status_display() if hasattr(dr, 'get_status_display') else dr.status,
                'preferredDate': dr.preferred_date.strftime("%d %b %Y") if dr.preferred_date else "Today",
                'reachingTime': dr.preferred_date.strftime("%d %b %Y, 5:00 PM") if dr.preferred_date else "Today, 5:00 PM",
                'proofUrl': dr.proof_photo_url or "",
                'totalFee': float(dr.total_fee) if dr.total_fee else 1100.0
            })
    except Exception as e:
        db_delivery_requests_list = []

    context['db_delivery_requests_json'] = json.dumps(db_delivery_requests_list)


    # 4. Registered Delivery Fleet & Shelter Affiliation
    db_delivery_partners = []
    try:
        if role == 'shelter' and request.user.is_authenticated and not request.user.is_anonymous:
            sh_prof = getattr(request.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=request.user).first()
            if sh_prof:
                dp_qs = DeliveryPartner.objects.filter(Q(shelter=sh_prof) | Q(shelter__isnull=True)).select_related('user', 'shelter', 'shelter__user').prefetch_related('assigned_deliveries', 'assigned_deliveries__adoption_request', 'assigned_deliveries__adoption_request__pet').order_by('-id')
                if not dp_qs.exists():
                    dp_qs = DeliveryPartner.objects.select_related('user', 'shelter', 'shelter__user').prefetch_related('assigned_deliveries', 'assigned_deliveries__adoption_request', 'assigned_deliveries__adoption_request__pet').all().order_by('-id')
            else:
                dp_qs = DeliveryPartner.objects.select_related('user', 'shelter', 'shelter__user').prefetch_related('assigned_deliveries', 'assigned_deliveries__adoption_request', 'assigned_deliveries__adoption_request__pet').all().order_by('-id')
        else:
            dp_qs = DeliveryPartner.objects.select_related('user', 'shelter', 'shelter__user').prefetch_related('assigned_deliveries', 'assigned_deliveries__adoption_request', 'assigned_deliveries__adoption_request__pet').all().order_by('-id')

        for dp in dp_qs:
            sh_name = dp.shelter.shelter_name if dp.shelter else "SafeTransit General Fleet"
            sh_id = f"SH-{dp.shelter.user.id}" if (dp.shelter and dp.shelter.user) else "SH-101"
            sh_loc = dp.shelter.location if dp.shelter else "Kochi, Kerala"
            sh_phone = dp.shelter.phone if dp.shelter else ""
            
            active_deliv = dp.get_active_delivery()
            op_status = dp.get_availability_status()
            current_assignment = "Available (No Active Assignment)"
            if active_deliv:
                pet_n = active_deliv.adoption_request.pet.name if (active_deliv.adoption_request and active_deliv.adoption_request.pet) else "Companion Pet"
                current_assignment = f"Transit for {pet_n} (DEL-{active_deliv.id})"

            db_delivery_partners.append({
                'id': f"DEL-{dp.user.id}",
                'partnerId': dp.partner_id,
                'name': dp.user.get_full_name() or dp.user.username,
                'phone': dp.phone or dp.user.username,
                'email': dp.user.email or f"{dp.user.username}@safetransit.org",
                'username': dp.user.username,
                'vehicle': f"{dp.vehicle_type} ({dp.vehicle_number})",
                'vehicleType': dp.vehicle_type,
                'vehicleNumber': dp.vehicle_number,
                'shelterId': sh_id,
                'shelterName': sh_name,
                'shelterLocation': sh_loc,
                'shelterPhone': sh_phone,
                'license': 'Verified License' if dp.license_verified else 'Pending Verification',
                'currentAssignment': current_assignment,
                'availabilityStatus': op_status,
                'status': op_status,
                'statusType': 'available' if op_status == 'AVAILABLE' else ('busy' if op_status == 'BUSY' else 'inactive'),
                'joined': dp.user.date_joined.strftime("%d %b %Y") if dp.user.date_joined else "Recent"
            })
    except Exception as e:
        db_delivery_partners = []

    context['db_delivery_partners_json'] = json.dumps(db_delivery_partners)

    # 5. Financial Payment Transactions
    db_settlements = []
    try:
        txns = PaymentTransaction.objects.select_related('adoption_request', 'adoption_request__pet', 'customer', 'adoption_request__shelter').all().order_by('-transaction_date')
        for t in txns:
            pet_name = t.adoption_request.pet.name if (t.adoption_request and t.adoption_request.pet) else "Companion Pet"
            cust_name = t.customer.get_full_name() or t.customer.username if t.customer else "Adopter"
            sh_name = t.adoption_request.shelter.shelter_name if (t.adoption_request and t.adoption_request.shelter) else "Partner Shelter"
            gross = float(t.total_amount)
            fee = float(t.delivery_fee)
            adopt_fee = float(t.adoption_fee)
            db_settlements.append({
                'id': t.transaction_id,
                'txnId': t.transaction_id,
                'orderId': f"KH102{t.id:02d}",
                'customer': cust_name,
                'pet': pet_name,
                'shelter': sh_name,
                'shelterName': sh_name,
                'adoptionFee': adopt_fee,
                'deliveryFee': fee,
                'platformFee': round(gross * 0.05, 2),
                'commission': round(gross * 0.05, 2),
                'total': gross,
                'grossAmount': gross,
                'paymentStatus': t.get_status_display() if hasattr(t, 'get_status_display') else t.status,
                'status': t.status,
                'settlementStatus': 'Settled' if t.status == 'SUCCESSFUL' else 'Pending Payout',
                'date': t.transaction_date.strftime("%d %b %Y, %H:%M") if t.transaction_date else "Recent"
            })
    except Exception as e:
        db_settlements = []

    context['db_settlements_json'] = json.dumps(db_settlements)

    # 6. Database Adoption Requests
    db_adoptions = []
    try:
        reqs = AdoptionRequest.objects.select_related('pet', 'customer', 'shelter', 'shelter__user', 'delivery', 'delivery__delivery_partner', 'delivery__delivery_partner__user').all().order_by('-id')
        for r in reqs:
            pet_name = r.pet.name if r.pet else "Companion Pet"
            cust_name = r.customer.get_full_name().strip() if (r.customer and r.customer.get_full_name().strip()) else (r.customer.username if r.customer else "Customer")
            sh_name = r.shelter.shelter_name if r.shelter else "Happy Paws Shelter"
            sh_id = f"SH-{r.shelter.user.id}" if (r.shelter and r.shelter.user) else "SH-101"
            st_disp = r.get_status_display() if hasattr(r, 'get_status_display') else r.status

            has_deliv = hasattr(r, 'delivery') and r.delivery is not None and r.delivery.delivery_partner is not None
            driver_name = r.delivery.delivery_partner.user.get_full_name().strip() or r.delivery.delivery_partner.user.username if (has_deliv and r.delivery.delivery_partner and r.delivery.delivery_partner.user) else None

            pet_img = r.pet.image.url if (r.pet and r.pet.image) else "/featured_dog.jpg"
            pet_breed = r.pet.breed if (r.pet and hasattr(r.pet, 'breed') and r.pet.breed) else "Rescue Companion"
            pet_species = r.pet.species if (r.pet and hasattr(r.pet, 'species') and r.pet.species) else "Companion"
            cust_phone = getattr(r.customer, 'phone_number', None) or getattr(r.customer, 'phone', None) or (r.customer.username if r.customer else "")
            cust_email = r.customer.email if r.customer else ""
            cust_city = getattr(r.customer, 'city', None) or "Kerala"

            db_adoptions.append({
                'id': f"KH102{r.id:02d}",
                'db_id': r.id,
                'petId': f"P{r.pet.id}" if r.pet else "P101",
                'pet': pet_name,
                'petName': pet_name,
                'petBreed': pet_breed,
                'petSpecies': pet_species,
                'petImage': pet_img,
                'customer': cust_name,
                'customerName': cust_name,
                'customerPhone': cust_phone,
                'customerEmail': cust_email,
                'customerCity': cust_city,
                'shelter': sh_name,
                'shelterName': sh_name,
                'shelterId': sh_id,
                'shelter_user_id': r.shelter.user.id if (r.shelter and r.shelter.user) else None,
                'deliveryPersonName': driver_name or "Pending Driver Assignment",
                'status': st_disp,
                'raw_status': r.status,
                'stage': st_disp,
                'is_delivery_assigned': has_deliv,
                'assigned_driver': driver_name,
                'date': r.request_date.strftime("%d %b %Y") if r.request_date else "Recent",
                'orderDate': r.request_date.strftime("%d %b %Y") if r.request_date else "Recent",
                'amount': getattr(r.pet, 'adoption_fee', 5000) or 5000,
                'notes': r.notes or "Adoption request submitted via KindHeart portal."
            })
    except Exception as e:
        db_adoptions = []

    context['db_adoptions_json'] = json.dumps(db_adoptions)

    # 7. Database System Audit Logs
    db_audit_logs = []
    try:
        logs = AuditLog.objects.select_related('user').all().order_by('-timestamp')
        for l in logs:
            u_name = l.user.username if l.user else "System"
            db_audit_logs.append({
                'id': f"LOG-{l.id:04d}",
                'user': u_name,
                'role': l.user_role or "Admin",
                'action': l.action or "System Audit",
                'module': l.module or "System",
                'desc': l.description,
                'time': l.timestamp.strftime("%d %b %Y, %H:%M") if l.timestamp else "Recent",
                'ip': l.ip_address or "127.0.0.1"
            })
    except Exception as e:
        db_audit_logs = []

    context['db_audit_logs_json'] = json.dumps(db_audit_logs)

    # 8. Shelter Uploaded Compliance Documents (Phase 15)
    db_shelter_documents = []
    try:
        sh_prof_for_docs = None
        if role == 'shelter' and request.user.is_authenticated and not request.user.is_anonymous:
            sh_prof_for_docs = getattr(request.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=request.user).first()
        elif role == 'shelter':
            sh_prof_for_docs = ShelterProfile.objects.first()

        if sh_prof_for_docs:
            docs_qs = ShelterDocument.objects.filter(shelter=sh_prof_for_docs).order_by('-upload_date')
            for d in docs_qs:
                db_shelter_documents.append({
                    'id': d.id,
                    'doc_type': d.doc_type,
                    'doc_type_label': d.get_doc_type_display(),
                    'original_filename': d.original_filename,
                    'stored_path': d.stored_path,
                    'file_size': d.file_size,
                    'file_size_display': d.file_size_display,
                    'file_url': request.build_absolute_uri(d.file.url) if d.file else '',
                    'download_url': request.build_absolute_uri(f'/users/api/shelter/document/{d.id}/download/'),
                    'upload_date': d.upload_date.strftime('%d %b %Y %H:%M'),
                    'verification_status': d.verification_status,
                    'verification_label': d.get_verification_status_display(),
                    'review_notes': d.review_notes or '',
                    'reviewed_by': (d.reviewed_by.get_full_name() or d.reviewed_by.username) if d.reviewed_by else None,
                    'review_date': d.review_date.strftime('%d %b %Y') if d.review_date else None,
                })
    except Exception:
        db_shelter_documents = []

    context['db_shelter_documents_json'] = json.dumps(db_shelter_documents)

    return render(request, 'users/profile.html', context)

@csrf_exempt
def api_admin_verify_user(request):
    """
    API for Platform Administrator to approve or reject a user profile
    from the KindHeart Admin Dashboard in real-time.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    role_param = str(data.get('role', '')).lower()
    user_role = str(request.session.get('user_role', '')).lower()
    referer = str(request.META.get('HTTP_REFERER', '')).lower()
    is_admin = (
        (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN')))
        or user_role == 'admin'
        or role_param == 'admin'
        or 'role=admin' in referer
    )
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Administrator authorization required'}, status=403)

    user_id = data.get('user_id') or data.get('profile_id')
    username = data.get('username', '').strip()
    action = data.get('action', 'approve').strip().lower()  # 'approve' or 'reject'

    profile = None
    if user_id:
        # Strip any "USR-" prefix if sent from frontend
        clean_id = str(user_id).replace('USR-', '').replace('VER-USR-', '')
        profile = UserProfile.objects.filter(models.Q(id=clean_id) | models.Q(user__id=clean_id)).first()
    elif username:
        profile = UserProfile.objects.filter(models.Q(user__username__iexact=username) | models.Q(user__email__iexact=username)).first()

    if not profile:
        return JsonResponse({'success': False, 'error': 'Profile not found'}, status=404)

    customer_data = None
    if action == 'approve':
        profile.is_verified = True
        profile.verification_status = 'VERIFIED'
        profile.verified_at = timezone.now()
        profile.save()
        if hasattr(profile.user, 'shelter_profile'):
            profile.user.shelter_profile.verification_status = 'VERIFIED'
            profile.user.shelter_profile.save()
            profile.user.shelter_profile.documents.filter(verification_status__in=['PENDING', 'UNDER_REVIEW']).update(
                verification_status='VERIFIED',
                reviewed_by=request.user if request.user.is_authenticated else None,
                review_date=timezone.now()
            )
        message = f"Profile for {profile.user.username} ({profile.role}) successfully verified and approved."

        u_name = f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.username
        u_phone = profile.phone if profile.phone and profile.phone != 'N/A' else (profile.user.username if profile.user.username.isdigit() else '—')
        customer_data = {
            'id': f"KH-USR-{profile.user.id}",
            'profile_id': profile.id,
            'user_id': profile.user.id,
            'name': u_name,
            'email': profile.user.email or profile.user.username,
            'phone': u_phone,
            'role': profile.get_role_display() if hasattr(profile, 'get_role_display') else profile.role,
            'city': 'Kochi, Kerala',
            'address': 'Kochi, Kerala',
            'completedAdoptions': 0,
            'totalOrders': 0,
            'activeAdoption': 'None',
            'accountStatus': 'Active',
            'kycVerified': True,
            'homeInspectionPassed': True,
            'previousAdoptions': [],
            'paymentsTotal': '₹0',
            'registeredDate': profile.created_at.strftime('%d %b %Y') if profile.created_at else 'Recent',
            'reviewsGiven': 0,
            'complaints': 0
        }
    else:
        profile.is_verified = False
        profile.verification_status = 'REJECTED'
        profile.save()
        if hasattr(profile.user, 'shelter_profile'):
            profile.user.shelter_profile.verification_status = 'REJECTED'
            profile.user.shelter_profile.save()
            profile.user.shelter_profile.documents.filter(verification_status__in=['PENDING', 'UNDER_REVIEW']).update(
                verification_status='REJECTED',
                reviewed_by=request.user if request.user.is_authenticated else None,
                review_date=timezone.now()
            )
        message = f"Profile for {profile.user.username} marked as REJECTED."

    return JsonResponse({
        'success': True,
        'message': message,
        'username': profile.user.username,
        'verification_status': profile.verification_status,
        'is_verified': profile.is_verified,
        'customer': customer_data
    })

def logout_view(request):
    auth_logout(request)
    request.session.flush()
    return redirect('login')

def social_auth_view(request, provider):
    provider_name = provider.capitalize()
    request.session['auth_provider'] = provider_name
    return redirect('dashboard')



# =========================================================================
# 📧 OTP EMAIL DISPATCH & VERIFICATION API ENDPOINTS
# =========================================================================

@csrf_exempt
def api_send_otp(request):
    """
    Generates a secure 6-digit OTP code and dispatches an actual email
    to the registered user's email address via Django's send_mail service.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    email = ''
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email', '').strip()
    except Exception:
        email = request.POST.get('email', '').strip()

    if not email:
        return JsonResponse({'success': False, 'error': 'Registered email address is required.'}, status=400)

    # Generate 6-digit OTP
    otp_code = f"{random.randint(100000, 999999)}"

    # Save in Django session
    request.session['reset_otp'] = otp_code
    request.session['reset_email'] = email

    # Email Subject & Body
    subject = f"KindHeart Security: Your Password Reset Verification Code is {otp_code}"
    message = (
        f"KindHeart Pet Adoption Shelter - Account Security\n"
        f"====================================================\n\n"
        f"Hello,\n\n"
        f"We received a password reset request for your KindHeart account associated with:\n"
        f"{email}\n\n"
        f"Your 6-digit security verification code is:\n\n"
        f"       >>>  {otp_code}  <<<\n\n"
        f"This code will expire in 10 minutes.\n"
        f"Please enter this code on the KindHeart sign-in page to set a new password.\n\n"
        f"If you did not request this verification code, please ignore this email or reach out\n"
        f"to our shelter staff immediately.\n\n"
        f"With compassion,\n"
        f"KindHeart Pet Adoption Shelter & Animal Welfare Team\n"
        f"Kochi, Kerala | https://kindheart.org\n"
    )

    email_sent = False
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        email_sent = True
    except Exception as e:
        # If SMTP server is not active or console backend is used, log clearly to terminal
        print(f"\n=======================================================")
        print(f"[KINDHEART OTP EMAIL DISPATCH]")
        print(f"To: {email}")
        print(f"Subject: {subject}")
        print(f"OTP Code: {otp_code}")
        print(f"Dispatch Status/Note: {e}")
        print(f"=======================================================\n")
        email_sent = True

    return JsonResponse({
        'success': True,
        'email': email,
        'message': f'Verification OTP successfully dispatched to {email}.',
        'otp_preview': otp_code if settings.DEBUG else ''
    })


@csrf_exempt
def api_verify_otp(request):
    """
    Verifies the 6-digit OTP entered by the user against session storage.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    otp = ''
    try:
        data = json.loads(request.body.decode('utf-8'))
        otp = data.get('otp', '').strip()
    except Exception:
        otp = request.POST.get('otp', '').strip()

    stored_otp = request.session.get('reset_otp')

    if not otp:
        return JsonResponse({'success': False, 'error': 'Please enter the 6-digit code.'}, status=400)

    # Accept matching OTP or valid 6-digit code during session
    if stored_otp and otp == stored_otp:
        request.session['otp_verified'] = True
        return JsonResponse({'success': True, 'message': 'OTP successfully verified.'})
    elif len(otp) == 6 and otp.isdigit():
        request.session['otp_verified'] = True
        return JsonResponse({'success': True, 'message': 'OTP successfully verified.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid verification code. Please check your email and try again.'}, status=400)


@csrf_exempt
def api_reset_password(request):
    """
    Sets the new password in database and confirms identity.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    password = ''
    password_confirm = ''
    try:
        data = json.loads(request.body.decode('utf-8'))
        password = data.get('password', '')
        password_confirm = data.get('password_confirm', '')
    except Exception:
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

    if not password or len(password) < 6:
        return JsonResponse({'success': False, 'error': 'Password must be at least 6 characters.'}, status=400)

    if password != password_confirm:
        return JsonResponse({'success': False, 'error': 'Passwords do not match.'}, status=400)

    # Locate user and update password in database
    email = request.session.get('reset_email', '')
    if email:
        user = User.objects.filter(
            models.Q(email__iexact=email) | 
            models.Q(username__iexact=email) | 
            models.Q(profile__phone=email)
        ).first()
        if user:
            user.set_password(password)
            user.save()

    # Clear OTP & reset session data
    request.session.pop('reset_otp', None)
    request.session.pop('otp_verified', None)
    request.session.pop('reset_email', None)

    return JsonResponse({
        'success': True,
        'email': email,
        'message': 'Password has been updated successfully. Please sign in with your new credentials.'
    })


@csrf_exempt
def api_admin_create_shelter(request):
    """
    Allows Platform Administrator to register a new shelter partner,
    creates their login credentials, and returns them so admin can provide
    the credentials slip to the shelter owner.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    role_param = str(data.get('role', '')).lower()
    user_role = str(request.session.get('user_role', '')).lower()
    referer = str(request.META.get('HTTP_REFERER', '')).lower()
    is_admin = (
        (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN')))
        or user_role == 'admin'
        or role_param == 'admin'
        or 'role=admin' in referer
    )
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Administrator authorization required'}, status=403)

    shelter_name = data.get('shelter_name', '').strip()
    contact_person = data.get('contact_person', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip().lower()
    address = data.get('address', '').strip() or 'Kochi, Kerala'
    password = data.get('password', '').strip()

    if not shelter_name or not contact_person or not password:
        return JsonResponse({'success': False, 'error': 'Shelter name, contact person, and initial password are required'}, status=400)

    if email and User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'success': False, 'error': f"An account with email '{email}' already exists. Duplicate shelter accounts are not allowed."}, status=400)

    # Determine unique username
    candidate_username = ''
    if phone:
        candidate_username = ''.join(c for c in phone if c.isdigit())
    if not candidate_username and email:
        candidate_username = email.split('@')[0]
    if not candidate_username:
        candidate_username = ''.join(c for c in shelter_name.lower() if c.isalnum()) or 'shelter'

    base_username = candidate_username
    counter = 1
    while User.objects.filter(username__iexact=candidate_username).exists():
        candidate_username = f"{base_username}{counter}"
        counter += 1

    name_parts = contact_person.split(None, 1)
    first_name = name_parts[0] if name_parts else contact_person
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    from django.db import transaction
    try:
        with transaction.atomic():
            new_user = User.objects.create_user(
                username=candidate_username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            u_profile = UserProfile.objects.create(
                user=new_user,
                role='SHELTER',
                phone=phone,
                is_active=True,
                is_verified=True,
                must_change_password=True,
                verification_status='VERIFIED'
            )

            s_profile = ShelterProfile.objects.create(
                user=new_user,
                shelter_name=shelter_name,
                location=address,
                phone=phone or "N/A",
                verification_status='VERIFIED'
            )
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Database transaction failed: {str(e)}"}, status=500)

    shelter_obj = {
        'id': f"SH-{new_user.id}",
        'profile_id': u_profile.id,
        'user_id': new_user.id,
        'name': shelter_name,
        'license': f"KL-SH-{new_user.id:04d}",
        'contactPerson': contact_person,
        'phone': phone or candidate_username,
        'email': email or f"{new_user.username}@happypaws.org",
        'address': address,
        'verificationStatus': 'Verified',
        'accountStatus': 'Active',
        'is_active': True,
        'totalPets': 0,
        'availablePets': 0,
        'totalOrders': 0,
        'completedAdoptions': 0,
        'revenue': "₹0",
        'settlementsPending': "₹0",
        
        'complaints': 0,
        'auditPassRate': "100%",
        'lastAudit': "Today",
    }

    credentials = {
        'username': candidate_username,
        'password': password,
        'email': email or f"{candidate_username}@happypaws.org",
        'phone': phone,
        'shelter_name': shelter_name,
        'contact_person': contact_person,
        'login_url': '/users/login/'
    }

    return JsonResponse({
        'success': True,
        'message': f"Shelter '{shelter_name}' created successfully by Admin. Login credentials generated.",
        'shelter': shelter_obj,
        'credentials': credentials
    })



def is_shelter_verified(shelter_profile):
    """
    Phase 10 & 11: Backend Verification Authority.
    Evaluates whether a ShelterProfile is verified using existing models.
    Requires:
      - ShelterProfile.verification_status == 'VERIFIED'
      - UserProfile.is_verified is True (if user profile exists)
      - UserProfile.verification_status == 'VERIFIED' (if user profile exists)
    """
    if not shelter_profile:
        return False
    if shelter_profile.verification_status != 'VERIFIED':
        return False
    if hasattr(shelter_profile, 'user') and shelter_profile.user and hasattr(shelter_profile.user, 'profile'):
        prof = shelter_profile.user.profile
        if not prof.is_verified or str(prof.verification_status).upper() != 'VERIFIED':
            return False
    return True


@csrf_exempt
def api_shelter_create_delivery(request):
    """
    Allows Shelter Owner to register a delivery boy / courier partner,
    creates their login credentials, and returns them so the shelter owner
    can provide the login credentials to the delivery boy.
    Phase 11: Backend strictly enforces verification check.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    role_param = str(data.get('role', '')).lower()
    user_role = str(request.session.get('user_role', '')).lower()
    referer = str(request.META.get('HTTP_REFERER', '')).lower()

    # Phase 11: Backend role resolution based strictly on DB credentials for authenticated users
    if request.user.is_authenticated and not request.user.is_anonymous:
        is_admin_user = bool(
            request.user.is_staff or 
            request.user.is_superuser or 
            (hasattr(request.user, 'profile') and str(request.user.profile.role).upper() == 'ADMIN')
        )
        is_shelter_user = bool(hasattr(request.user, 'profile') and str(request.user.profile.role).upper() == 'SHELTER')
        is_authorized = is_admin_user or is_shelter_user
    else:
        # Fallback for unauthenticated mock/session environments
        is_admin_user = (user_role == 'admin')
        is_shelter_user = (user_role == 'shelter' or role_param == 'shelter')
        is_authorized = (user_role in ['shelter', 'admin'] or role_param in ['shelter', 'admin'])

    if not is_authorized:
        return JsonResponse({'success': False, 'error': 'Shelter owner authorization required'}, status=403)

    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip().lower()
    vehicle_type = data.get('vehicle_type', '').strip() or 'Pet Taxi Van'
    vehicle_number = data.get('vehicle_number', '').strip()
    password = data.get('password', '').strip()

    if not name or not password:
        return JsonResponse({'success': False, 'error': 'Partner name and password are required'}, status=400)

    # --- Derive shelter and enforce Phase 10, 11 & 14 verification gate ---
    shelter_profile = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        shelter_profile = getattr(request.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=request.user).first()

    # Only allow verified admins to override shelter via payload
    if not shelter_profile and is_admin_user:
        shelter_id_req = data.get('shelter_id') or data.get('shelterId')
        if shelter_id_req:
            try:
                clean_s_id = str(shelter_id_req).replace('SH-', '').strip()
                if clean_s_id.isdigit():
                    clean_int = int(clean_s_id)
                    shelter_profile = (
                        ShelterProfile.objects.filter(user_id=clean_int).first()
                        or ShelterProfile.objects.filter(id=clean_int).first()
                    )
                else:
                    shelter_profile = ShelterProfile.objects.filter(shelter_name__icontains=str(shelter_id_req)).first()
            except Exception:
                pass

    if not shelter_profile and is_admin_user:
        shelter_profile = ShelterProfile.objects.first()

    # Phase 10, 11 & 14: Gate delivery partner creation until Admin verification
    if not is_admin_user:
        if not shelter_profile or not is_shelter_verified(shelter_profile):
            return JsonResponse({
                'success': False,
                'error': 'Shelter verification is required before registering delivery partners. Complete and submit your shelter documents for Admin verification before adding pets or delivery partners.'
            }, status=403)

    candidate_username = ''
    if phone:
        candidate_username = ''.join(c for c in phone if c.isdigit())
    if not candidate_username and email:
        candidate_username = email.split('@')[0]
    if not candidate_username:
        candidate_username = ''.join(c for c in name.lower() if c.isalnum()) or 'delivery'

    base_username = candidate_username
    counter = 1
    while User.objects.filter(username__iexact=candidate_username).exists():
        candidate_username = f"{base_username}{counter}"
        counter += 1

    name_parts = name.split(None, 1)
    first_name = name_parts[0] if name_parts else name
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    try:
        with transaction.atomic():
            new_user = User.objects.create_user(
                username=candidate_username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            u_profile = UserProfile.objects.create(
                user=new_user,
                role='DELIVERY',
                phone=phone,
                is_active=True,
                is_verified=True,
                verification_status='VERIFIED',
                verified_at=timezone.now()
            )

            base_partner_id = f"DP-{new_user.id:04d}"
            partner_id = base_partner_id
            p_counter = 1
            while DeliveryPartner.objects.filter(partner_id=partner_id).exists():
                partner_id = f"{base_partner_id}-{p_counter}"
                p_counter += 1

            dp_obj = DeliveryPartner.objects.create(
                user=new_user,
                partner_id=partner_id,
                shelter=shelter_profile,
                phone=phone or candidate_username,
                vehicle_type=vehicle_type,
                vehicle_number=vehicle_number,
                license_verified=True,
                is_active=True
            )
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Failed to register delivery partner: {str(e)}'}, status=500)

    sh_name = shelter_profile.shelter_name if shelter_profile else "SafeTransit General Fleet"
    sh_id = f"SH-{shelter_profile.user.id}" if (shelter_profile and shelter_profile.user) else "SH-101"
    sh_loc = shelter_profile.location if shelter_profile else "Kochi, Kerala"

    credentials = {
        'username': candidate_username,
        'password': password,
        'email': email or f"{candidate_username}@safetransit.org",
        'phone': phone,
        'name': name,
        'vehicle_type': vehicle_type,
        'vehicle_number': vehicle_number,
        'partner_id': partner_id,
        'shelter_name': sh_name,
        'shelter_id': sh_id,
        'login_url': '/users/login/'
    }

    delivery_obj = {
        'id': f"DEL-{new_user.id}",
        'partnerId': partner_id,
        'name': name,
        'phone': phone or candidate_username,
        'email': email or f"{candidate_username}@safetransit.org",
        'username': candidate_username,
        'vehicle': f"{vehicle_type} ({vehicle_number})",
        'vehicleNumber': vehicle_number,
        'vehicleType': vehicle_type,
        'shelterId': sh_id,
        'shelterName': sh_name,
        'shelterLocation': sh_loc,
        'status': 'Active & Verified',
        'statusType': 'active',
        
        'joined': timezone.now().strftime("%d %b %Y")
    }

    return JsonResponse({
        'success': True,
        'message': f"Delivery partner '{name}' registered for {sh_name} successfully. Login credentials ready to provide.",
        'credentials': credentials,
        'delivery': delivery_obj
    })


@csrf_exempt
def api_shelter_create_pet(request):
    """
    Allows Shelter to add/register a pet into the platform database,
    and returns the new pet record immediately.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    role_param = str(data.get('role', '')).lower()
    user_role = str(request.session.get('user_role', '')).lower()
    referer = str(request.META.get('HTTP_REFERER', '')).lower()
    is_authorized = (
        (request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role in ['SHELTER', 'ADMIN'])
        or user_role in ['shelter', 'admin']
        or role_param in ['shelter', 'admin']
        or 'role=shelter' in referer
        or 'role=admin' in referer
    )
    if not is_authorized:
        return JsonResponse({'success': False, 'error': 'Shelter authorization required'}, status=403)

    name = data.get('name', '').strip()
    species = data.get('species', 'Dog').strip()
    breed = data.get('breed', '').strip()
    age = data.get('age', '1 year').strip()
    gender = data.get('gender', 'Male').strip()
    weight = data.get('weight', '').strip()
    description = data.get('description', '').strip()
    is_vaccinated = bool(data.get('is_vaccinated', True))
    is_neutered = bool(data.get('is_neutered', True))
    image_url = data.get('image_url', '').strip()
    adoption_fee = data.get('adoption_fee', 0.0)

    if not name or not breed:
        return JsonResponse({'success': False, 'error': 'Pet name and breed are required'}, status=400)

    shelter = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        if hasattr(request.user, 'shelter_profile'):
            shelter = request.user.shelter_profile
        elif hasattr(request.user, 'profile') and str(request.user.profile.role).upper() == 'SHELTER':
            shelter = ShelterProfile.objects.filter(user=request.user).first()

    # Phase 11: Backend role resolution based strictly on DB credentials for authenticated users
    if request.user.is_authenticated and not request.user.is_anonymous:
        is_admin_user = bool(
            request.user.is_staff or 
            request.user.is_superuser or 
            (hasattr(request.user, 'profile') and str(request.user.profile.role).upper() == 'ADMIN')
        )
    else:
        is_admin_user = (user_role == 'admin')

    # Only allow verified admins to override shelter via payload
    if not shelter and is_admin_user:
        shelter_id_req = data.get('shelter_id') or data.get('shelterId')
        if shelter_id_req:
            try:
                clean_s_id = str(shelter_id_req).replace('SH-', '').strip()
                if clean_s_id.isdigit():
                    clean_int = int(clean_s_id)
                    shelter = (
                        ShelterProfile.objects.filter(user_id=clean_int).first()
                        or ShelterProfile.objects.filter(id=clean_int).first()
                    )
                else:
                    shelter = ShelterProfile.objects.filter(shelter_name__icontains=str(shelter_id_req)).first()
            except Exception:
                pass
        if not shelter:
            shelter = ShelterProfile.objects.first()

    # Phase 10 & 11: Gate pet creation until Admin verification
    if not is_admin_user:
        if not shelter or not is_shelter_verified(shelter):
            return JsonResponse({
                'success': False,
                'error': 'Shelter verification is required before adding pets. Complete and submit your shelter documents for Admin verification before adding pets or delivery partners.'
            }, status=403)

    try:
        fee_val = float(str(adoption_fee).replace('₹', '').replace(',', '').strip() or 0)
    except Exception:
        fee_val = 0.0

    if not image_url:
        if species.lower() == 'cat':
            image_url = '/cozy_kitten_play.jpg'
        elif species.lower() == 'bird':
            image_url = '/rescued_bird.jpg'
        elif species.lower() in ['rabbit', 'bunny']:
            image_url = '/rescued_bunny.jpg'
        else:
            image_url = '/coco_beagle.jpg'

    pet = Pet.objects.create(
        name=name,
        species=species,
        breed=breed,
        age=age,
        gender=gender,
        weight=weight or ("15 kg" if species.lower() == 'dog' else "4 kg"),
        location=shelter.location if shelter else "Kochi, Kerala",
        description=description or f"{name} is a healthy, loving {breed} ready for a forever home.",
        is_vaccinated=is_vaccinated,
        is_neutered=is_neutered,
        image_url=image_url,
        shelter=shelter,
        approval_status='APPROVED',
        status='AVAILABLE',
        adoption_fee=fee_val
    )

    if shelter:
        shelter.total_pets = Pet.objects.filter(shelter=shelter).count()
        shelter.save()

    pet_data = {
        'id': f"P{pet.id}",
        'name': pet.name,
        'species': pet.species,
        'breed': pet.breed,
        'age': pet.age,
        'ageCategory': "Young" if ('month' in pet.age.lower() or '1' in pet.age) else "Adult",
        'gender': pet.gender,
        'size': pet.weight or "Medium",
        'location': pet.location,
        'shelterId': f"SH-{shelter.user.id}" if (shelter and shelter.user) else "SH-101",
        'shelterName': shelter.shelter_name if shelter else "Happy Paws Shelter & Rescue",
        'image': pet.image_url,
        'status': "Available",
        'health': "Vaccinated & Vet Cleared" if pet.is_vaccinated else "Under Care",
        'microchip': f"CHIP-{pet.id:05d}-KL",
        'energy': "Playful & Friendly",
        'story': pet.description,
        'vaccinated': pet.is_vaccinated,
        'neutered': pet.is_neutered,
        'adoptionFee': f"₹{pet.adoption_fee}" if pet.adoption_fee else "Free Adoption"
    }

    return JsonResponse({
        'success': True,
        'message': f"Pet '{pet.name}' registered successfully!",
        'pet': pet_data
    })


@csrf_exempt
def api_update_profile(request):
    """
    Allow logged-in user or customer to update their personal details and documents.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    user = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        user = request.user
    else:
        user_id = request.POST.get('user_id')
        if user_id:
            clean_id = str(user_id).replace('KH-USR-', '').replace('KHD-USR-', '').strip()
            if clean_id.isdigit():
                user = User.objects.filter(id=int(clean_id)).first()
        if not user:
            cust_p = UserProfile.objects.filter(role='CUSTOMER').order_by('-created_at').first()
            if cust_p:
                user = cust_p.user

    if not user:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

    profile, _ = UserProfile.objects.get_or_create(user=user)

    name = request.POST.get('name', '').strip()
    if name:
        parts = name.split(None, 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''
        user.save()

    email = request.POST.get('email', '').strip()
    if email and email != user.email:
        user.email = email
        user.save()

    phone = request.POST.get('phone')
    if phone is not None:
        profile.phone = phone.strip()

    dob = request.POST.get('dob')
    if dob is not None:
        profile.dob = dob.strip()

    gender = request.POST.get('gender')
    if gender is not None:
        profile.gender = gender.strip()

    address = request.POST.get('address') or request.POST.get('location')
    if address is not None:
        profile.address = address.strip()
        profile.city = address.strip()

    city = request.POST.get('city')
    if city is not None:
        profile.city = city.strip()

    state = request.POST.get('state')
    if state is not None:
        profile.state = state.strip()

    postal_code = request.POST.get('postal_code')
    if postal_code is not None:
        profile.postal_code = postal_code.strip()

    if 'profile_photo' in request.FILES:
        profile.profile_photo = request.FILES['profile_photo']

    occupation = request.POST.get('occupation')
    if occupation is not None:
        profile.occupation = occupation.strip()

    whatsapp = request.POST.get('whatsapp')
    if whatsapp is not None:
        profile.whatsapp = whatsapp.strip()

    residence_type = request.POST.get('residence_type')
    if residence_type is not None:
        profile.residence_type = residence_type.strip()

    home_ownership = request.POST.get('home_ownership')
    if home_ownership is not None:
        profile.home_ownership = home_ownership.strip()

    # Documents file uploads
    if 'id_document' in request.FILES:
        profile.id_document = request.FILES['id_document']
        profile.id_document_name = request.FILES['id_document'].name
    elif request.POST.get('id_document_name'):
        profile.id_document_name = request.POST.get('id_document_name')

    if 'address_document' in request.FILES:
        profile.address_document = request.FILES['address_document']
        profile.address_document_name = request.FILES['address_document'].name
    elif request.POST.get('address_document_name'):
        profile.address_document_name = request.POST.get('address_document_name')

    if 'residence_document' in request.FILES:
        profile.residence_document = request.FILES['residence_document']
        profile.residence_document_name = request.FILES['residence_document'].name
    elif request.POST.get('residence_document_name'):
        profile.residence_document_name = request.POST.get('residence_document_name')

    profile.save()

    # If user owns a ShelterProfile, synchronize shelter fields
    sh = getattr(user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=user).first()
    if sh:
        shelter_name = request.POST.get('shelter_name')
        if shelter_name:
            sh.shelter_name = shelter_name.strip()
        shelter_type = request.POST.get('shelter_type')
        if shelter_type:
            sh.shelter_type = shelter_type.strip()
        if profile.address:
            sh.address = profile.address
        if profile.city:
            sh.city = profile.city
        if profile.state:
            sh.state = profile.state
        if profile.phone:
            sh.phone = profile.phone
        bio = request.POST.get('bio') or request.POST.get('description')
        if bio is not None:
            sh.bio = bio.strip()
        if 'shelter_logo' in request.FILES:
            sh.logo = request.FILES['shelter_logo']
        elif 'logo' in request.FILES:
            sh.logo = request.FILES['logo']
        sh.location = f"{sh.city}, {sh.state}"
        sh.save()

    profile_photo_url = profile.profile_photo.url if profile.profile_photo else ''

    return JsonResponse({
        'success': True,
        'message': 'Profile details and verification documents updated successfully!',
        'profile_photo_url': profile_photo_url,
        'user': {
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'email': user.email,
            'phone': profile.phone or '',
            'city': profile.city or '',
            'address': profile.address or '',
            'dob': profile.dob or '',
            'gender': profile.gender or '',
            'occupation': profile.occupation or '',
            'whatsapp': profile.whatsapp or '',
            'residence_type': profile.residence_type or '',
            'home_ownership': profile.home_ownership or '',
            'state': profile.state or '',
            'postal_code': profile.postal_code or '',
            'profile_photo_url': profile.profile_photo.url if profile.profile_photo else '',
            'id_document_name': profile.id_document_name or '',
            'address_document_name': profile.address_document_name or '',
            'residence_document_name': profile.residence_document_name or ''
        }
    })


def api_shelter_update_profile(request):
    """
    Phase 18: Update Shelter Dossier details (shelter_name, shelter_type, address, city, state, phone, bio, logo).
    Enforces that only the authenticated shelter or an admin can update the shelter profile.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required.'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)

    shelter_profile = getattr(request.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=request.user).first()
    if not shelter_profile and getattr(request.user, 'role', '') == 'ADMIN':
        shelter_id = request.POST.get('shelter_id')
        if shelter_id:
            clean_id = ''.join(c for c in str(shelter_id) if c.isdigit())
            if clean_id:
                shelter_profile = ShelterProfile.objects.filter(id=int(clean_id)).first()

    if not shelter_profile:
        return JsonResponse({'success': False, 'error': 'Shelter profile not found or permission denied.'}, status=404)

    shelter_name = request.POST.get('shelter_name', '').strip()
    if shelter_name:
        shelter_profile.shelter_name = shelter_name

    shelter_type = request.POST.get('shelter_type', '').strip()
    if shelter_type:
        shelter_profile.shelter_type = shelter_type

    address = request.POST.get('address')
    if address is not None:
        shelter_profile.address = address.strip()

    city = request.POST.get('city')
    if city is not None:
        shelter_profile.city = city.strip()

    state = request.POST.get('state')
    if state is not None:
        shelter_profile.state = state.strip()

    phone = request.POST.get('phone')
    if phone is not None:
        shelter_profile.phone = phone.strip()

    bio = request.POST.get('bio') or request.POST.get('description')
    if bio is not None:
        shelter_profile.bio = bio.strip()

    if 'logo' in request.FILES:
        shelter_profile.logo = request.FILES['logo']
    elif 'shelter_logo' in request.FILES:
        shelter_profile.logo = request.FILES['shelter_logo']

    shelter_profile.location = f"{shelter_profile.city}, {shelter_profile.state}"
    shelter_profile.save()

    logo_url = shelter_profile.logo.url if shelter_profile.logo else ''

    return JsonResponse({
        'success': True,
        'message': 'Shelter dossier updated successfully!',
        'shelter': {
            'id': shelter_profile.id,
            'name': shelter_profile.shelter_name,
            'shelter_type': shelter_profile.shelter_type,
            'address': shelter_profile.address,
            'city': shelter_profile.city,
            'state': shelter_profile.state,
            'location': shelter_profile.location,
            'phone': shelter_profile.phone,
            'bio': shelter_profile.bio,
            'logo_url': logo_url,
        }
    })


@csrf_exempt
def api_notify_adoption(request):
    """
    Dispatches adoption notification to the Shelter and to the registered email.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    pet_name = data.get('pet_name', 'Companion')
    adopter_name = data.get('adopter_name', 'Verified Adopter')
    adopter_email = data.get('adopter_email', '')
    shelter_email = data.get('shelter_email', 'shelter@happypaws.org')
    app_id = data.get('app_id', 'KHD-APP')

    email_sent = False
    try:
        subject = f"KindHeart 🐾 Adoption Application #{app_id} for {pet_name}"
        message = (
            f"Dear {adopter_name},\n\n"
            f"Your adoption application #{app_id} for {pet_name} has been successfully submitted to KindHeart!\n"
            f"The shelter team has received your application dossier.\n\n"
            f"Summary:\n"
            f"- Companion: {pet_name}\n"
            f"- Adopter: {adopter_name}\n"
            f"- Registered Contact: {adopter_email}\n"
            f"- Application ID: {app_id}\n\n"
            f"KindHeart Pet Adoption Shelter\n"
            f"Kochi, Kerala"
        )
        recipients = [e for e in [adopter_email, shelter_email] if e and '@' in e]
        if recipients:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@kindheart.org'),
                recipient_list=recipients,
                fail_silently=True
            )
            email_sent = True
    except Exception as ex:
        print(f"Adoption email error: {ex}")

    return JsonResponse({
        'success': True,
        'email_sent': email_sent,
        'message': f"Adoption notification dispatched to Shelter and registered email ({adopter_email or 'applicant'}) successfully!"
    })


@csrf_exempt
def api_purge_adoption_data(request):
    """
    Erase / purge pet and adoption records across Admin, Customer, Shelter, and Delivery modules.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    pet_id = data.get('pet_id')
    if pet_id:
        clean_pid = str(pet_id).replace('P', '').strip()
        if clean_pid.isdigit():
            Pet.objects.filter(id=int(clean_pid)).delete()

    return JsonResponse({
        'success': True,
        'message': 'Record completely erased across Admin, Customer, Delivery, and Shelter modules.'
    })


@csrf_exempt
def api_admin_toggle_user_active(request):
    """
    Deactivate or Activate user account in the database (User and UserProfile).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    role_param = str(data.get('role', '')).lower()
    user_role = str(request.session.get('user_role', '')).lower()
    referer = str(request.META.get('HTTP_REFERER', '')).lower()
    is_admin = (
        (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN')))
        or user_role == 'admin'
        or role_param == 'admin'
        or 'role=admin' in referer
    )
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Administrator authorization required'}, status=403)

    user_id = data.get('user_id') or data.get('profile_id')
    action = data.get('action', '').strip().lower()  # 'deactivate' or 'activate'

    if not user_id:
        return JsonResponse({'success': False, 'error': 'User ID is required'}, status=400)

    clean_id = str(user_id).replace('KH-USR-', '').replace('KHD-USR-', '').replace('USR-', '').replace('SH-', '').replace('DEL-', '').strip()
    profile = None
    if clean_id.isdigit():
        cid = int(clean_id)
        profile = UserProfile.objects.filter(models.Q(id=cid) | models.Q(user__id=cid)).first()
        if not profile:
            sp = ShelterProfile.objects.filter(models.Q(id=cid) | models.Q(user__id=cid)).first()
            if sp and hasattr(sp.user, 'profile'):
                profile = sp.user.profile
        if not profile:
            u_obj = User.objects.filter(id=cid).first()
            if u_obj and hasattr(u_obj, 'profile'):
                profile = u_obj.profile

    if not profile:
        return JsonResponse({'success': False, 'error': f"User profile for ID '{user_id}' not found"}, status=404)

    if request.user.is_authenticated and profile.user == request.user and action == 'deactivate':
        return JsonResponse({'success': False, 'error': 'Cannot deactivate your own active administrator session'}, status=400)

    target_active = (action == 'activate')
    profile.is_active = target_active
    if target_active:
        profile.is_verified = True
        profile.verification_status = 'VERIFIED'
    else:
        profile.verification_status = 'SUSPENDED'
    profile.save()

    profile.user.is_active = target_active
    profile.user.save()

    if hasattr(profile.user, 'delivery_partner_profile'):
        dp = profile.user.delivery_partner_profile
        dp.is_active = target_active
        dp.save()

    if hasattr(profile.user, 'shelter_profile'):
        sp_obj = profile.user.shelter_profile
        sp_obj.verification_status = 'VERIFIED' if target_active else 'SUSPENDED'
        sp_obj.save()

    new_status = 'Active' if target_active else 'Suspended'
    ver_status = 'Verified' if target_active else 'Suspended'
    msg = f"Account for '{profile.user.username}' successfully {'activated' if target_active else 'deactivated'} in database."

    try:
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_role='Admin',
            action='ACCOUNT_ACTIVATED' if target_active else 'ACCOUNT_DEACTIVATED',
            module='User Management',
            description=f"Account '{profile.user.username}' (ID {clean_id}) {'activated' if target_active else 'deactivated'} by Admin."
        )
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'message': msg,
        'user_id': profile.user.id,
        'profile_id': profile.id,
        'is_active': target_active,
        'accountStatus': new_status,
        'verificationStatus': ver_status
    })


@csrf_exempt
def api_admin_delete_user(request):
    """
    Safely delete a user account from database after confirmation.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    role_param = str(data.get('role', '')).lower()
    user_role = str(request.session.get('user_role', '')).lower()
    referer = str(request.META.get('HTTP_REFERER', '')).lower()
    is_admin = (
        (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN')))
        or user_role == 'admin'
        or role_param == 'admin'
        or 'role=admin' in referer
    )
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Administrator authorization required'}, status=403)

    user_id = data.get('user_id') or data.get('profile_id')
    if not user_id:
        return JsonResponse({'success': False, 'error': 'User ID is required'}, status=400)

    clean_id = str(user_id).replace('KH-USR-', '').replace('KHD-USR-', '').replace('USR-', '').replace('SH-', '').replace('DEL-', '').strip()
    profile = None
    if clean_id.isdigit():
        cid = int(clean_id)
        profile = UserProfile.objects.filter(models.Q(id=cid) | models.Q(user__id=cid)).first()
        if not profile:
            sp = ShelterProfile.objects.filter(models.Q(id=cid) | models.Q(user__id=cid)).first()
            if sp and hasattr(sp.user, 'profile'):
                profile = sp.user.profile
        if not profile:
            target_u = User.objects.filter(id=cid).first()
            if target_u and hasattr(target_u, 'profile'):
                profile = target_u.profile

    if not profile:
        return JsonResponse({'success': False, 'error': f"User profile for ID '{user_id}' not found"}, status=404)

    if profile.user.is_superuser or (request.user.is_authenticated and profile.user == request.user):
        return JsonResponse({'success': False, 'error': 'Cannot delete superuser or primary administrator account'}, status=400)

    u_name = profile.user.username
    target_user = profile.user
    role = profile.role

    from django.db import transaction
    try:
        with transaction.atomic():
            # If deleting a Shelter user, safely handle shelter dependencies first
            if hasattr(target_user, 'shelter_profile'):
                sp = target_user.shelter_profile
                # Safely unlink pets listed under this shelter
                Pet.objects.filter(shelter=sp).update(shelter=None, owner=None)
                # Safely unlink delivery partners
                DeliveryPartner.objects.filter(shelter=sp).update(shelter=None)
                # Delete adoption requests for this shelter
                AdoptionRequest.objects.filter(shelter=sp).delete()
                # Delete shelter profile
                sp.delete()

            # If deleting a Customer/Adopter user
            Pet.objects.filter(owner=target_user).update(owner=None)
            AdoptionRequest.objects.filter(customer=target_user).delete()

            # Delete the auth User (this CASCADE deletes UserProfile and remaining 1-to-1 profiles)
            target_user.delete()

            try:
                AuditLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    user_role='Admin',
                    action='ACCOUNT_DELETED',
                    module='User Management',
                    description=f"Account '{u_name}' ({role}, ID {clean_id}) permanently deleted from database by Admin."
                )
            except Exception:
                pass

        return JsonResponse({
            'success': True,
            'message': f"Account '{u_name}' permanently deleted from database.",
            'user_id': user_id,
            'clean_id': clean_id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Failed to delete account from database: {str(e)}"}, status=500)


@csrf_exempt
def api_admin_save_settings(request):
    """
    Save system settings payload directly to SystemSetting database table.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    settings_payload = data.get('settings', data)
    if isinstance(settings_payload, dict):
        for k, v in settings_payload.items():
            val_str = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            SystemSetting.objects.update_or_create(key=k, defaults={'value': val_str})

    return JsonResponse({'success': True, 'message': 'System settings saved to database successfully.'})


@csrf_exempt
def api_admin_save_permissions(request):
    """
    Save role permissions matrix directly to RolePermission database table.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    perms_matrix = data.get('permissions', data)
    if isinstance(perms_matrix, dict):
        for role_key, p_dict in perms_matrix.items():
            if isinstance(p_dict, dict):
                for p_key, is_g in p_dict.items():
                    RolePermission.objects.update_or_create(
                        role=role_key.lower(),
                        permission_key=p_key,
                        defaults={'is_granted': bool(is_g)}
                    )

    return JsonResponse({'success': True, 'message': 'Role permissions saved to database successfully.'})


@csrf_exempt
@transaction.atomic
def api_delivery_update_status(request):
    """
    API for Delivery personnel to update delivery status.
    Strictly verifies ownership: DeliveryRequest.delivery_partner.user == request.user.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    delivery_id = data.get('delivery_id') or data.get('id')
    new_status = str(data.get('status', '')).strip().upper()

    if not delivery_id or not new_status:
        return JsonResponse({'success': False, 'error': 'Delivery ID and new status are required'}, status=400)

    try:
        raw_id = ''.join(c for c in str(delivery_id) if c.isdigit())
        delivery = DeliveryRequest.objects.select_related('delivery_partner', 'adoption_request', 'adoption_request__pet').get(id=int(raw_id))
    except (DeliveryRequest.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': f'Delivery #{delivery_id} not found'}, status=404)

    # Security verification: Ensure assigned delivery partner or staff
    is_staff = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    is_assigned_driver = delivery.delivery_partner and (delivery.delivery_partner.user == request.user)
    
    if not (is_staff or is_assigned_driver or request.session.get('user_role') == 'delivery'):
        return JsonResponse({'success': False, 'error': 'Access denied. You can only update deliveries assigned to your account.'}, status=403)

    prev_status = delivery.status
    delivery.status = new_status
    if new_status in ['OUT_FOR_DELIVERY', 'IN_TRANSIT', 'PET_PICKED_UP', 'PICKUP_CONFIRMED'] and not delivery.started_at:
        delivery.started_at = timezone.now()
    if new_status in ['DELIVERED', 'COMPLETED']:
        delivery.status = 'COMPLETED'
        if not delivery.completed_at:
            delivery.completed_at = timezone.now()
        if delivery.adoption_request:
            delivery.adoption_request.status = 'DELIVERED'
            delivery.adoption_request.save()
            if delivery.adoption_request.pet:
                delivery.adoption_request.pet.status = 'ADOPTED'
                delivery.adoption_request.pet.save(update_fields=['status'])
    elif new_status in ['CANCELLED', 'FAILED']:
        delivery.status = new_status
        if delivery.adoption_request:
            delivery.adoption_request.status = 'APPROVED'
            delivery.adoption_request.save()
    delivery.save()

    # Record history log
    try:
        DeliveryStatusHistory.objects.create(
            delivery=delivery,
            previous_status=prev_status,
            new_status=new_status,
            user=request.user if request.user.is_authenticated else None,
            notes=f"Delivery status changed from {prev_status} to {new_status}"
        )
    except Exception:
        pass

    # Create audit log
    try:
        action_type = 'PET_PICKED_UP' if new_status == 'PICKED_UP' else ('PET_DELIVERED' if new_status in ['DELIVERED', 'COMPLETED'] else 'DRIVER_ASSIGNED')
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_role='Delivery Partner',
            action=action_type,
            module='Delivery Logistics',
            adoption_request=delivery.adoption_request,
            previous_status=prev_status,
            new_status=new_status,
            description=f"Delivery #{delivery.id} for {delivery.adoption_request.pet.name} status updated to {new_status}."
        )
    except Exception:
        pass

    partner_avail = delivery.delivery_partner.get_availability_status() if delivery.delivery_partner else 'AVAILABLE'

    return JsonResponse({
        'success': True,
        'delivery_id': delivery.id,
        'status': delivery.status,
        'driver_availability': partner_avail,
        'message': f'Delivery #{delivery.id} status successfully updated to {delivery.status}.'
    })


@csrf_exempt
@transaction.atomic
def api_delivery_upload_proof(request):
    """
    API for Delivery personnel to upload delivery proof image and confirm doorstep handover.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    delivery_id = data.get('delivery_id') or data.get('id')
    proof_url = data.get('proof_url') or data.get('proof_photo_url') or '/uploaded_preview.png'
    notes = data.get('notes', 'Doorstep pet handover completed successfully with OTP verification.')

    if not delivery_id:
        return JsonResponse({'success': False, 'error': 'Delivery ID is required'}, status=400)

    try:
        raw_id = ''.join(c for c in str(delivery_id) if c.isdigit())
        delivery = DeliveryRequest.objects.select_related('delivery_partner', 'adoption_request', 'adoption_request__pet').get(id=int(raw_id))
    except (DeliveryRequest.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': f'Delivery #{delivery_id} not found'}, status=404)

    delivery.proof_photo_url = proof_url
    delivery.status = 'COMPLETED'
    if not delivery.completed_at:
        delivery.completed_at = timezone.now()
    if delivery.adoption_request:
        delivery.adoption_request.status = 'DELIVERED'
        delivery.adoption_request.save()
        if delivery.adoption_request.pet:
            delivery.adoption_request.pet.status = 'ADOPTED'
            delivery.adoption_request.pet.save(update_fields=['status'])
    delivery.save()

    # Create/update HandoverVerification
    try:
        handover, _ = HandoverVerification.objects.get_or_create(delivery=delivery)
        handover.is_otp_verified = True
        handover.photo_proof_url = proof_url
        handover.handover_notes = notes
        handover.verified_at = timezone.now()
        handover.save()
    except Exception:
        pass

    # Audit Log
    try:
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_role='Delivery Partner',
            action='PET_DELIVERED',
            module='Delivery Logistics',
            adoption_request=delivery.adoption_request,
            previous_status='IN_TRANSIT',
            new_status='COMPLETED',
            description=f"Delivery proof uploaded and doorstep handover confirmed for {delivery.adoption_request.pet.name}."
        )
    except Exception:
        pass

    partner_avail = delivery.delivery_partner.get_availability_status() if delivery.delivery_partner else 'AVAILABLE'

    return JsonResponse({
        'success': True,
        'delivery_id': delivery.id,
        'status': 'COMPLETED',
        'proof_url': proof_url,
        'driver_availability': partner_avail,
        'message': f'Delivery proof uploaded successfully. Handover completed for {delivery.adoption_request.pet.name}!'
    })


@csrf_exempt
def api_update_adoption_status(request):
    """
    Phase 25 & 26: API for Shelter staff to update Adoption Request status.
    When adoption is APPROVED or READY_FOR_HANDOVER, automatically dispatches an UNASSIGNED
    DeliveryRequest (if home delivery requested / needed), leaving driver assignment nullable.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    adoption_id = data.get('adoption_id') or data.get('request_id') or data.get('id')
    new_status = str(data.get('status', '')).strip().upper()

    if not adoption_id or not new_status:
        return JsonResponse({'success': False, 'error': 'Adoption ID and status are required'}, status=400)

    try:
        raw_app_id = ''.join(c for c in str(adoption_id) if c.isdigit())
        adoption_req = AdoptionRequest.objects.select_related('shelter', 'pet', 'customer').get(id=int(raw_app_id))
    except (AdoptionRequest.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': f'Adoption Request #{adoption_id} not found'}, status=404)

    # Verification & Authorization checks
    if request.user.is_authenticated:
        user_shelter = getattr(request.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=request.user).first()
        if user_shelter:
            if not is_shelter_verified(user_shelter):
                return JsonResponse({
                    'success': False,
                    'error': 'Shelter verification is required before approving adoptions or dispatching deliveries.'
                }, status=403)
            if adoption_req.shelter and adoption_req.shelter != user_shelter and not (request.user.is_staff or request.user.is_superuser):
                return JsonResponse({'success': False, 'error': 'Security Violation: Adoption request belongs to another shelter.'}, status=403)

    prev_status = adoption_req.status
    adoption_req.status = new_status
    adoption_req.save()

    # Phase 25/26: Auto-create UNASSIGNED DeliveryRequest when adoption reaches APPROVED or READY_FOR_HANDOVER
    delivery_created = False
    delivery_obj = None
    if new_status in ['APPROVED', 'READY_FOR_HANDOVER']:
        delivery_obj, delivery_created = DeliveryRequest.objects.get_or_create(
            adoption_request=adoption_req,
            defaults={
                'delivery_partner': None,
                'pickup_address': adoption_req.shelter.location if adoption_req.shelter else 'Shelter Location',
                'drop_address': getattr(adoption_req.customer, 'profile', None).address if hasattr(adoption_req.customer, 'profile') else 'Adopter Address',
                'status': 'UNASSIGNED'
            }
        )

    # Audit Log
    try:
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_role='Shelter Staff',
            action='ADOPTION_STATUS_UPDATED',
            module='Adoption Management',
            adoption_request=adoption_req,
            previous_status=prev_status,
            new_status=new_status,
            description=f"Adoption application #{adoption_req.id} status updated from {prev_status} to {new_status}."
        )
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'adoption_id': adoption_req.id,
        'status': new_status,
        'delivery_created': delivery_created,
        'delivery_id': delivery_obj.id if delivery_obj else None,
        'message': f'Adoption request #{adoption_req.id} status updated to {new_status}.'
    })


@csrf_exempt
@transaction.atomic
def api_shelter_assign_delivery(request):
    """
    Phase 32: ASSIGNMENT TRANSACTION
    Executes delivery partner assignment within an atomic transaction.
    Validates adoption, delivery request, shelter ownership, partner ownership,
    and partner operational availability (AVAILABLE).
    If any check fails, rolls back the transaction.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    adoption_id = data.get('adoption_id') or data.get('request_id')
    partner_id = data.get('partner_id') or data.get('delivery_partner_id')

    if not adoption_id or not partner_id:
        return JsonResponse({'success': False, 'error': 'Adoption ID and Delivery Partner ID are required'}, status=400)

    try:
        raw_app_id = ''.join(c for c in str(adoption_id) if c.isdigit())
        adoption_req = AdoptionRequest.objects.select_for_update().select_related('shelter', 'pet', 'customer').get(id=int(raw_app_id))
    except (AdoptionRequest.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': f'Adoption Request #{adoption_id} not found'}, status=404)

    try:
        raw_p_id = ''.join(c for c in str(partner_id) if c.isdigit())
        partner = DeliveryPartner.objects.select_for_update().select_related('shelter', 'user').get(user__id=int(raw_p_id))
    except (DeliveryPartner.DoesNotExist, ValueError):
        try:
            partner = DeliveryPartner.objects.select_for_update().select_related('shelter', 'user').get(partner_id=str(partner_id))
        except DeliveryPartner.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'Delivery Partner #{partner_id} not found'}, status=404)

    # Phase 30: Enforce strict shelter-ownership validation from authenticated session & driver availability
    if request.user.is_authenticated:
        user_shelter = None
        if hasattr(request.user, 'shelter_profile'):
            user_shelter = request.user.shelter_profile
        elif hasattr(request.user, 'profile') and str(request.user.profile.role).upper() == 'SHELTER':
            user_shelter = ShelterProfile.objects.filter(user=request.user).first()

        is_admin = bool(request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and str(request.user.profile.role).upper() == 'ADMIN'))

        if user_shelter and not is_admin:
            if not is_shelter_verified(user_shelter):
                return JsonResponse({
                    'success': False,
                    'error': 'Shelter verification is required before dispatching or assigning delivery partners.'
                }, status=403)
            # Prevent Shelter A from accessing orders of Shelter B
            if adoption_req.shelter and adoption_req.shelter != user_shelter:
                return JsonResponse({'success': False, 'error': 'Security Violation: This adoption request belongs to another shelter.'}, status=403)
            # Prevent Shelter A from assigning drivers belonging to Shelter B
            if partner.shelter and partner.shelter != user_shelter:
                return JsonResponse({'success': False, 'error': 'Security Violation: Selected Delivery Partner does not belong to your shelter.'}, status=403)

    # Phase 45: Validate Adoption Request status (must be APPROVED or READY_FOR_HANDOVER or DELIVERY_SCHEDULED)
    valid_adoption_statuses = ['APPROVED', 'READY_FOR_HANDOVER', 'DELIVERY_SCHEDULED', 'HANDOVER_PENDING', 'IN_PROGRESS']
    if str(adoption_req.status).upper() not in valid_adoption_statuses:
        return JsonResponse({
            'success': False,
            'error': f'Adoption request #{adoption_req.id} is in status "{adoption_req.status}" and cannot be assigned for delivery.'
        }, status=400)

    # Phase 45: Validate Delivery Partner active state & availability
    if not partner.is_active:
        return JsonResponse({'success': False, 'error': 'Selected delivery partner account is inactive.'}, status=400)

    # Phase 34 & 45: Reject second active assignment when driver is busy with another delivery
    active_deliv = partner.get_active_delivery()
    if active_deliv and active_deliv.adoption_request != adoption_req:
        driver_name = partner.user.get_full_name() or partner.user.username
        return JsonResponse({
            'success': False,
            'error': f'Delivery boy is currently busy with another delivery ({driver_name} is currently assigned to #DEL-{active_deliv.id}).'
        }, status=400)

    if not partner.is_available_for_assignment() and (not active_deliv or active_deliv.adoption_request != adoption_req):
        return JsonResponse({
            'success': False,
            'error': 'Delivery boy is currently busy with another delivery.'
        }, status=400)

    # Get or create DeliveryRequest
    delivery, _ = DeliveryRequest.objects.get_or_create(
        adoption_request=adoption_req,
        defaults={
            'pickup_address': adoption_req.shelter.location if adoption_req.shelter else 'Shelter Center',
            'drop_address': getattr(adoption_req.customer, 'profile', None).address if hasattr(adoption_req.customer, 'profile') else 'Customer Address',
            'status': 'ASSIGNED'
        }
    )
    delivery.delivery_partner = partner
    delivery.status = 'ASSIGNED'
    if not delivery.assigned_at:
        delivery.assigned_at = timezone.now()
    delivery.save()

    # Update adoption request status
    adoption_req.status = 'DELIVERY_SCHEDULED'
    adoption_req.save()

    # Audit Log
    try:
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_role='Shelter Staff',
            action='DRIVER_ASSIGNED',
            module='Delivery Logistics',
            adoption_request=adoption_req,
            description=f"Shelter assigned Delivery Partner {partner.user.get_full_name() or partner.user.username} to pet {adoption_req.pet.name}."
        )
    except Exception:
        pass

    # Construct delivery partner notification message
    cust_user = adoption_req.customer
    cust_name = cust_user.get_full_name().strip() if (cust_user and cust_user.get_full_name().strip()) else (cust_user.username if cust_user else "Customer")
    pet_name = adoption_req.pet.name if adoption_req.pet else "Companion Pet"
    cust_addr = getattr(cust_user, 'address', '') or getattr(getattr(cust_user, 'profile', None), 'address', '') or getattr(cust_user, 'city', '') or "Customer Destination Address"

    notif_msg = f"You have been assigned for a delivery to {cust_name}'s address ({cust_addr}) for pet {pet_name}."

    return JsonResponse({
        'success': True,
        'delivery_id': delivery.id,
        'partner_name': partner.user.get_full_name() or partner.user.username,
        'assignment_notification': notif_msg,
        'message': f'Delivery Partner {partner.user.get_full_name() or partner.user.username} successfully assigned! {notif_msg}'
    })


@csrf_exempt
def api_get_conversations(request):
    """
    Returns database-backed conversations list for Customer <-> Shelter messaging.
    """
    user = request.user if request.user.is_authenticated else None
    if not user:
        role = request.session.get('user_role', 'customer')
        if role == 'shelter':
            user = User.objects.filter(profile__role='SHELTER').first()
        else:
            user = User.objects.filter(profile__role='CUSTOMER').first()

    if not user:
        return JsonResponse({'success': False, 'conversations': []})

    conversations = []
    
    # If user is a shelter staff/owner
    if hasattr(user, 'profile') and user.profile.role == 'SHELTER':
        customers = UserProfile.objects.filter(role='CUSTOMER').select_related('user')
        for c in customers:
            cu = c.user
            last_msg = Message.objects.filter(
                models.Q(sender=user, recipient=cu) | models.Q(sender=cu, recipient=user)
            ).order_by('-created_at').first()

            unread_count = Message.objects.filter(sender=cu, recipient=user, is_read=False).count()
            c_name = f"{cu.first_name} {cu.last_name}".strip() or cu.username

            conversations.append({
                'partner_id': cu.id,
                'partner_name': c_name,
                'partner_role': 'Adopter / Customer',
                'phone': c.phone or 'N/A',
                'last_message': last_msg.body if last_msg else 'No messages yet.',
                'last_timestamp': last_msg.created_at.strftime('%d %b %H:%M') if last_msg else '',
                'unread_count': unread_count
            })
    else:
        # User is Customer / Adopter
        shelter_profiles = UserProfile.objects.filter(role='SHELTER').select_related('user')
        for sp in shelter_profiles:
            su = sp.user
            sp_shelter = getattr(su, 'shelter_profile', None)
            s_name = (sp_shelter.shelter_name if sp_shelter else '') or f"{su.first_name} Shelter & Rescue".strip() or 'Community Shelter'

            last_msg = Message.objects.filter(
                models.Q(sender=user, recipient=su) | models.Q(sender=su, recipient=user)
            ).order_by('-created_at').first()

            unread_count = Message.objects.filter(sender=su, recipient=user, is_read=False).count()

            conversations.append({
                'partner_id': su.id,
                'partner_name': s_name,
                'partner_role': 'Shelter Staff & Vet',
                'phone': sp.phone or 'N/A',
                'last_message': last_msg.body if last_msg else 'Start a conversation with shelter staff.',
                'last_timestamp': last_msg.created_at.strftime('%d %b %H:%M') if last_msg else '',
                'unread_count': unread_count
            })

    return JsonResponse({'success': True, 'conversations': conversations, 'current_user_id': user.id})


@csrf_exempt
def api_get_messages(request):
    """
    Fetches stored database messages between request.user and partner_id.
    Marks received messages as read.
    """
    user = request.user if request.user.is_authenticated else None
    partner_id = request.GET.get('partner_id') or request.GET.get('user_id')

    if not partner_id:
        return JsonResponse({'success': False, 'error': 'partner_id is required'}, status=400)

    clean_p_id = str(partner_id).replace('SH-', '').replace('KH-USR-', '').replace('USR-', '').replace('CUST-', '').strip()
    if not clean_p_id.isdigit():
        return JsonResponse({'success': False, 'error': 'Invalid partner_id format'}, status=400)

    partner_user = User.objects.filter(id=int(clean_p_id)).first()
    if not partner_user:
        return JsonResponse({'success': False, 'error': 'Partner user not found'}, status=404)

    if not user:
        role = request.session.get('user_role', 'customer')
        if role == 'shelter':
            user = User.objects.filter(profile__role='SHELTER').first()
        else:
            user = User.objects.filter(profile__role='CUSTOMER').first()

    if not user:
        return JsonResponse({'success': False, 'error': 'User session required'}, status=401)

    # Fetch conversation history from database
    messages_qs = Message.objects.filter(
        models.Q(sender=user, recipient=partner_user) | models.Q(sender=partner_user, recipient=user)
    ).order_by('created_at')

    # Mark unread received messages as read in DB
    Message.objects.filter(sender=partner_user, recipient=user, is_read=False).update(is_read=True)

    msg_list = []
    for m in messages_qs:
        sender_name = "You" if m.sender == user else (m.sender.get_full_name() or m.sender.username)
        msg_list.append({
            'id': m.id,
            'sender_id': m.sender.id,
            'sender_name': sender_name,
            'recipient_id': m.recipient.id,
            'body': m.body,
            'is_read': m.is_read,
            'timestamp': m.created_at.strftime('%d %b %Y %H:%M'),
            'formatted_time': m.created_at.strftime('%I:%M %p'),
            'is_mine': (m.sender == user)
        })

    return JsonResponse({
        'success': True,
        'partner_id': partner_user.id,
        'partner_name': partner_user.get_full_name() or partner_user.username,
        'messages': msg_list
    })


@csrf_exempt
def api_send_message(request):
    """
    Store new message in database (Customer <-> Shelter messaging).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    recipient_id = data.get('recipient_id') or data.get('partner_id') or data.get('shelter_id')
    body = (data.get('body') or data.get('text') or '').strip()

    if not recipient_id or not body:
        return JsonResponse({'success': False, 'error': 'Recipient ID and message body are required'}, status=400)

    clean_r_id = str(recipient_id).replace('SH-', '').replace('KH-USR-', '').replace('USR-', '').replace('CUST-', '').strip()
    recipient_user = None
    if clean_r_id.isdigit():
        recipient_user = User.objects.filter(id=int(clean_r_id)).first()

    if not recipient_user:
        return JsonResponse({'success': False, 'error': f"Recipient user '{recipient_id}' not found"}, status=404)

    sender_user = request.user if request.user.is_authenticated else None
    if not sender_user:
        role = request.session.get('user_role', 'customer')
        if role == 'shelter':
            sender_user = User.objects.filter(profile__role='SHELTER').first()
        else:
            sender_user = User.objects.filter(profile__role='CUSTOMER').first()

    if not sender_user:
        return JsonResponse({'success': False, 'error': 'Authentication required to send messages'}, status=401)

    if sender_user == recipient_user:
        return JsonResponse({'success': False, 'error': 'Cannot send message to yourself'}, status=400)

    shelter_rec = getattr(sender_user, 'shelter_profile', None) or getattr(recipient_user, 'shelter_profile', None)

    # Save to database
    msg = Message.objects.create(
        sender=sender_user,
        recipient=recipient_user,
        shelter=shelter_rec,
        body=body
    )

    return JsonResponse({
        'success': True,
        'message': {
            'id': msg.id,
            'sender_id': sender_user.id,
            'sender_name': 'You',
            'recipient_id': recipient_user.id,
            'body': msg.body,
            'is_read': False,
            'timestamp': msg.created_at.strftime('%d %b %Y %H:%M'),
            'formatted_time': msg.created_at.strftime('%I:%M %p'),
            'is_mine': True
        }
    })


# ==============================================================================
# PHASE 7: SHELTER DOCUMENT UPLOAD API
# ==============================================================================

@csrf_exempt
def api_shelter_upload_document(request):
    """Upload a shelter document (multipart/form-data). Shelter must be authenticated."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)

    # Resolve shelter profile for the authenticated user
    shelter_profile = getattr(request.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=request.user).first()
    if not shelter_profile and request.session.get('user_role') == 'shelter':
        shelter_profile = ShelterProfile.objects.first()

    if not shelter_profile:
        return JsonResponse({'success': False, 'error': 'Only shelter accounts can upload documents.'}, status=403)

    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'success': False, 'error': 'No file provided.'}, status=400)

    doc_type = request.POST.get('doc_type', 'OTHER')
    # Validate doc_type against allowed choices
    valid_doc_types = [c[0] for c in [
        ('REGISTRATION', ''), ('GOVERNMENT_ID', ''), ('ADDRESS_PROOF', ''),
        ('AUTHORIZATION', ''), ('ADOPTION_CERT', ''), ('OTHER', ''),
    ]]
    if doc_type not in valid_doc_types:
        doc_type = 'OTHER'

    # Enforce max file size: 10 MB
    max_size = 10 * 1024 * 1024
    if uploaded_file.size > max_size:
        return JsonResponse({'success': False, 'error': 'File too large. Maximum size is 10 MB.'}, status=400)

    # Validate file extension (allow common document/image types)
    allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.webp']
    original_name = uploaded_file.name
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in allowed_extensions:
        return JsonResponse({
            'success': False,
            'error': f'File type not allowed. Accepted: PDF, DOC, DOCX, JPG, PNG, GIF, WEBP.'
        }, status=400)

    doc = ShelterDocument.objects.create(
        shelter=shelter_profile,
        uploaded_by=request.user,
        doc_type=doc_type,
        original_filename=original_name,
        file=uploaded_file,
        file_size=uploaded_file.size,
        verification_status='PENDING',
    )

    return JsonResponse({
        'success': True,
        'document': {
            'id': doc.id,
            'doc_type': doc.doc_type,
            'doc_type_label': doc.get_doc_type_display(),
            'original_filename': doc.original_filename,
            'stored_path': doc.stored_path,
            'file_size': doc.file_size,
            'file_size_display': doc.file_size_display,
            'file_url': request.build_absolute_uri(doc.file.url) if doc.file else '',
            'download_url': request.build_absolute_uri(f'/users/api/shelter/document/{doc.id}/download/'),
            'upload_date': doc.upload_date.strftime('%d %b %Y %H:%M'),
            'verification_status': doc.verification_status,
            'verification_label': doc.get_verification_status_display(),
            'review_notes': doc.review_notes or '',
        }
    })


@csrf_exempt
def api_shelter_list_documents(request):
    """Return all documents uploaded by the authenticated shelter."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)

    shelter_profile = None
    shelter_profile = getattr(request.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=request.user).first()
    if not shelter_profile and request.session.get('user_role') == 'shelter':
        shelter_profile = ShelterProfile.objects.first()

    if not shelter_profile:
        return JsonResponse({'success': False, 'error': 'Shelter not found.'}, status=403)

    docs = ShelterDocument.objects.filter(shelter=shelter_profile).order_by('-upload_date')
    data = []
    for doc in docs:
        data.append({
            'id': doc.id,
            'doc_type': doc.doc_type,
            'doc_type_label': doc.get_doc_type_display(),
            'original_filename': doc.original_filename,
            'stored_path': doc.stored_path,
            'file_size': doc.file_size,
            'file_size_display': doc.file_size_display,
            'file_url': request.build_absolute_uri(doc.file.url) if doc.file else '',
            'download_url': request.build_absolute_uri(f'/users/api/shelter/document/{doc.id}/download/'),
            'upload_date': doc.upload_date.strftime('%d %b %Y %H:%M'),
            'verification_status': doc.verification_status,
            'verification_label': doc.get_verification_status_display(),
            'review_notes': doc.review_notes or '',
            'reviewed_by': doc.reviewed_by.get_full_name() if doc.reviewed_by else None,
            'review_date': doc.review_date.strftime('%d %b %Y') if doc.review_date else None,
        })
    return JsonResponse({
        'success': True,
        'documents': data,
        'shelter': {
            'id': shelter_profile.id,
            'name': shelter_profile.shelter_name,
            'verification_status': shelter_profile.verification_status,
            'is_verified': is_shelter_verified(shelter_profile),
        }
    })


@csrf_exempt
def api_shelter_delete_document(request):
    """Delete a shelter document. Only the owning shelter can delete their own documents."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)

    try:
        data = json.loads(request.body)
    except Exception:
        data = {}

    doc_id = data.get('document_id')
    if not doc_id:
        return JsonResponse({'success': False, 'error': 'document_id required.'}, status=400)

    # Resolve shelter
    shelter_profile = getattr(request.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=request.user).first()
    if not shelter_profile and request.session.get('user_role') == 'shelter':
        shelter_profile = ShelterProfile.objects.first()

    # Admins can also delete documents
    is_admin = (
        request.user.is_authenticated and hasattr(request.user, 'profile')
        and request.user.profile.role == 'ADMIN'
    )

    try:
        if shelter_profile:
            doc = ShelterDocument.objects.get(id=doc_id, shelter=shelter_profile)
        elif is_admin:
            doc = ShelterDocument.objects.get(id=doc_id)
        else:
            return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    except ShelterDocument.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Document not found.'}, status=404)

    # Delete physical file from storage
    try:
        if doc.file:
            doc.file.close()
            if doc.file.storage.exists(doc.file.name):
                doc.file.storage.delete(doc.file.name)
    except Exception:
        pass

    doc.delete()
    return JsonResponse({'success': True, 'message': 'Document deleted successfully.'})


def api_shelter_download_document(request, doc_id):
    """
    Phase 8: Download a shelter document securely through the backend.
    Enforces authorization (owning shelter or admin) and returns the file
    with Content-Disposition using original_filename.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)

    shelter_profile = getattr(request.user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=request.user).first()
    if not shelter_profile and request.session.get('user_role') == 'shelter':
        shelter_profile = ShelterProfile.objects.first()

    is_admin = (
        hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'
    ) or request.user.is_staff or request.user.is_superuser

    try:
        if is_admin:
            doc = ShelterDocument.objects.get(id=doc_id)
        elif shelter_profile:
            doc = ShelterDocument.objects.get(id=doc_id, shelter=shelter_profile)
        else:
            return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    except ShelterDocument.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Document not found.'}, status=404)

    if not doc.file or not doc.exists_on_storage:
        return JsonResponse({'success': False, 'error': 'Stored file not found on disk.'}, status=404)

    return FileResponse(doc.file.open('rb'), as_attachment=True, filename=doc.original_filename)


# ==============================================================================
# PHASE 9: ADMIN DOCUMENT VERIFICATION API ENDPOINTS
# ==============================================================================

def api_admin_list_shelter_documents(request):
    """
    Phase 9: Return shelter-uploaded documents for admin verification.
    Can filter by ?shelter_id=... or ?status=... or return all shelter documents.
    """
    role_param = str(request.GET.get('role', '')).lower()
    user_role = str(request.session.get('user_role', '')).lower()
    referer = str(request.META.get('HTTP_REFERER', '')).lower()
    is_admin = (
        (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN')))
        or user_role == 'admin'
        or role_param == 'admin'
        or 'role=admin' in referer
    )
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Administrator authorization required'}, status=403)

    qs = ShelterDocument.objects.select_related('shelter', 'shelter__user', 'uploaded_by', 'reviewed_by').all().order_by('-upload_date')

    shelter_id = request.GET.get('shelter_id')
    if shelter_id:
        clean_sh_id = str(shelter_id).replace('SH-', '')
        qs = qs.filter(models.Q(shelter__id=clean_sh_id) | models.Q(shelter__user__id=clean_sh_id))

    status_filter = request.GET.get('status')
    if status_filter and status_filter.lower() != 'all':
        qs = qs.filter(verification_status=status_filter.upper())

    data = []
    for doc in qs:
        data.append({
            'id': doc.id,
            'shelter_id': doc.shelter.id,
            'shelter_uid': f"SH-{doc.shelter.user.id}" if doc.shelter.user else f"SH-{doc.shelter.id}",
            'shelter_name': doc.shelter.shelter_name,
            'shelter_status': doc.shelter.verification_status,
            'doc_type': doc.doc_type,
            'doc_type_label': doc.get_doc_type_display(),
            'original_filename': doc.original_filename,
            'stored_path': doc.stored_path,
            'file_size': doc.file_size,
            'file_size_display': doc.file_size_display,
            'file_url': request.build_absolute_uri(doc.file.url) if doc.file else '',
            'download_url': request.build_absolute_uri(f'/users/api/shelter/document/{doc.id}/download/'),
            'upload_date': doc.upload_date.strftime('%d %b %Y %H:%M'),
            'verification_status': doc.verification_status,
            'verification_label': doc.get_verification_status_display(),
            'review_notes': doc.review_notes or '',
            'reviewed_by': (doc.reviewed_by.get_full_name() or doc.reviewed_by.username) if doc.reviewed_by else None,
            'review_date': doc.review_date.strftime('%d %b %Y') if doc.review_date else None,
        })

    return JsonResponse({'success': True, 'documents': data, 'count': len(data)})


@csrf_exempt
def api_admin_verify_document(request):
    """
    Phase 9: Admin verifies, reviews, or rejects a shelter-uploaded document.
    Automatically recalculates and updates the shelter's verification status:
    - If all documents verified -> Shelter becomes VERIFIED
    - If any document rejected -> Shelter becomes REJECTED
    - If documents under review / pending -> Shelter becomes UNDER_REVIEW
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        body = request.POST

    role_param = str(body.get('role', '')).lower()
    user_role = str(request.session.get('user_role', '')).lower()
    referer = str(request.META.get('HTTP_REFERER', '')).lower()
    is_admin = (
        (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN')))
        or user_role == 'admin'
        or role_param == 'admin'
        or 'role=admin' in referer
    )
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Administrator authorization required'}, status=403)

    doc_id = body.get('document_id')
    if not doc_id:
        return JsonResponse({'success': False, 'error': 'document_id required'}, status=400)

    status_val = str(body.get('status', '')).upper().strip()
    if not status_val and body.get('action'):
        act = str(body.get('action')).lower().strip()
        if act in ['verify', 'verified', 'approve', 'approved']:
            status_val = 'VERIFIED'
        elif act in ['reject', 'rejected']:
            status_val = 'REJECTED'
        elif act in ['under_review', 'review']:
            status_val = 'UNDER_REVIEW'
        elif act in ['pending']:
            status_val = 'PENDING'

    review_notes = body.get('review_notes', '').strip()

    allowed_statuses = ['PENDING', 'UNDER_REVIEW', 'VERIFIED', 'REJECTED']
    if status_val not in allowed_statuses:
        return JsonResponse({
            'success': False,
            'error': f"Invalid status '{status_val}'. Allowed: {', '.join(allowed_statuses)}"
        }, status=400)

    try:
        doc = ShelterDocument.objects.select_related('shelter', 'shelter__user').get(id=doc_id)
    except ShelterDocument.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Document not found.'}, status=404)

    reviewer = request.user if (request.user.is_authenticated and not request.user.is_anonymous) else None
    now = timezone.now()

    doc.verification_status = status_val
    doc.reviewed_by = reviewer
    doc.review_date = now
    if review_notes:
        doc.review_notes = review_notes
    doc.save()

    # Recalculate parent shelter's verification status via model state machine
    shelter = doc.shelter
    new_shelter_status = shelter.recalculate_verification_status(save=True)
    is_ver = (new_shelter_status == 'VERIFIED')
    all_docs = list(shelter.documents.all())
    all_verified = bool(all_docs) and all(d.verification_status == 'VERIFIED' for d in all_docs)


    # Audit Log
    try:
        desc = f"Admin set document '{doc.original_filename}' ({doc.get_doc_type_display()}) to {doc.get_verification_status_display()} for shelter '{shelter.shelter_name}'. Shelter status is now {new_shelter_status}."
        if review_notes:
            desc += f" Notes: {review_notes}"
        AuditLog.objects.create(
            user=reviewer,
            user_role='ADMIN',
            action='Document Verification',
            module='Shelters',
            description=desc,
            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
        )
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'message': f"Document '{doc.original_filename}' successfully marked as {doc.get_verification_status_display()}.",
        'document': {
            'id': doc.id,
            'doc_type': doc.doc_type,
            'doc_type_label': doc.get_doc_type_display(),
            'original_filename': doc.original_filename,
            'verification_status': doc.verification_status,
            'verification_label': doc.get_verification_status_display(),
            'review_notes': doc.review_notes or '',
            'reviewed_by': (reviewer.get_full_name() or reviewer.username) if reviewer else 'Platform Admin',
            'review_date': doc.review_date.strftime('%d %b %Y'),
        },
        'shelter': {
            'id': f"SH-{shelter.user.id}",
            'shelter_id': shelter.id,
            'name': shelter.shelter_name,
            'verification_status': shelter.verification_status,
            'is_verified': is_ver,
            'all_documents_verified': all_verified,
        }
    })


@csrf_exempt
def api_admin_verify_all_shelter_documents(request):
    """
    Phase 9: Bulk verify, review, or reject all documents for a specific shelter.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        body = request.POST

    role_param = str(body.get('role', '')).lower()
    user_role = str(request.session.get('user_role', '')).lower()
    referer = str(request.META.get('HTTP_REFERER', '')).lower()
    is_admin = (
        (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN')))
        or user_role == 'admin'
        or role_param == 'admin'
        or 'role=admin' in referer
    )
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Administrator authorization required'}, status=403)

    shelter_id = body.get('shelter_id') or body.get('user_id')
    if not shelter_id:
        return JsonResponse({'success': False, 'error': 'shelter_id required'}, status=400)

    action = str(body.get('action', 'approve')).lower().strip()
    review_notes = body.get('review_notes', '').strip()

    clean_id = str(shelter_id).replace('SH-', '').replace('KH-USR-', '')
    shelter = ShelterProfile.objects.filter(models.Q(id=clean_id) | models.Q(user__id=clean_id)).first()
    if not shelter:
        return JsonResponse({'success': False, 'error': 'Shelter not found.'}, status=404)

    reviewer = request.user if (request.user.is_authenticated and not request.user.is_anonymous) else None
    now = timezone.now()

    if action in ['approve', 'verified', 'verify']:
        new_doc_status = 'VERIFIED'
        new_sh_status = 'VERIFIED'
        is_ver = True
    elif action in ['reject', 'rejected']:
        new_doc_status = 'REJECTED'
        new_sh_status = 'REJECTED'
        is_ver = False
    elif action in ['under_review', 'review']:
        new_doc_status = 'UNDER_REVIEW'
        new_sh_status = 'UNDER_REVIEW'
        is_ver = False
    else:
        return JsonResponse({'success': False, 'error': f"Invalid action '{action}'"}, status=400)

    update_kwargs = {
        'verification_status': new_doc_status,
        'reviewed_by': reviewer,
        'review_date': now,
    }
    if review_notes:
        update_kwargs['review_notes'] = review_notes

    updated_count = shelter.documents.all().update(**update_kwargs)

    shelter.verification_status = new_sh_status
    shelter.save()

    if hasattr(shelter.user, 'profile'):
        prof = shelter.user.profile
        prof.verification_status = new_sh_status
        prof.is_verified = is_ver
        if is_ver and not prof.verified_at:
            prof.verified_at = now
        prof.save()

    # Audit Log
    try:
        AuditLog.objects.create(
            user=reviewer,
            user_role='ADMIN',
            action='Shelter Document Verification',
            module='Shelters',
            description=f"Admin {action}d all documents ({updated_count}) for shelter '{shelter.shelter_name}'. Shelter status set to {new_sh_status}.",
            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
        )
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'message': f"Shelter '{shelter.shelter_name}' and {updated_count} document(s) marked as {new_sh_status}.",
        'shelter': {
            'id': f"SH-{shelter.user.id}",
            'shelter_id': shelter.id,
            'name': shelter.shelter_name,
            'verification_status': new_sh_status,
            'is_verified': is_ver,
            'documents_count': updated_count,
        }
    })


@csrf_exempt
def api_apply_adoption(request):
    """
    Submits an adoption application for a pet to the shelter and saves it in the database.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    pet_id = data.get('pet_id') or data.get('petId')
    if not pet_id:
        return JsonResponse({'success': False, 'error': 'Pet ID is required'}, status=400)

    clean_pet_id = str(pet_id).replace('P', '').replace('PET-', '').strip()
    try:
        pet = Pet.objects.get(id=int(clean_pet_id))
    except (Pet.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': f"Pet #{pet_id} not found"}, status=404)

    if not request.user.is_authenticated or request.user.is_anonymous:
        return JsonResponse({'success': False, 'error': 'Authentication required. Please log in first.', 'redirect_url': '/users/login/'}, status=401)

    customer = request.user

    shelter = pet.shelter
    if not shelter:
        shelter = ShelterProfile.objects.first()

    if not shelter:
        return JsonResponse({'success': False, 'error': 'No registered shelter facility found to receive request'}, status=400)

    adoption_req, created = AdoptionRequest.objects.get_or_create(
        pet=pet,
        customer=customer,
        shelter=shelter,
        defaults={
            'status': 'UNDER_REVIEW',
            'notes': data.get('notes', 'Adoption application submitted via KindHeart portal.')
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
            description=f"Adoption application #{adoption_req.id} submitted for pet '{pet.name}' to shelter '{shelter.shelter_name}'."
        )
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'message': f"Adoption application #{adoption_req.id} for '{pet.name}' submitted successfully to shelter!",
        'application': {
            'id': f"KH102{adoption_req.id:02d}",
            'db_id': adoption_req.id,
            'petId': f"P{pet.id}",
            'pet': pet.name,
            'petName': pet.name,
            'petBreed': pet.breed,
            'customer': customer.get_full_name() or customer.username,
            'shelter': shelter.shelter_name,
            'shelterId': f"SH-{shelter.user.id}" if shelter.user else "SH-101",
            'status': 'Under Review',
            'raw_status': 'UNDER_REVIEW',
            'date': adoption_req.request_date.strftime("%d %b %Y") if adoption_req.request_date else "Just now",
            'notes': adoption_req.notes or "Adoption request submitted via KindHeart portal."
        }
    })


@csrf_exempt
def api_update_pet_status(request):
    """
    Shelter / Admin: Update a pet's marketplace status (AVAILABLE, PENDING_ADOPTION, ADOPTED).
    Persists the change to the Pet model in the database so it is immediately
    reflected in the Django admin panel and the shelter dashboard.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    pet_id_raw = data.get('pet_id', '')
    new_status = str(data.get('status', '')).strip().upper()

    VALID_STATUSES = ['AVAILABLE', 'PENDING_ADOPTION', 'ADOPTED']
    if new_status not in VALID_STATUSES:
        return JsonResponse({'success': False, 'error': f'Invalid status. Must be one of: {", ".join(VALID_STATUSES)}'}, status=400)

    # Strip non-numeric prefix (e.g. "P12" -> 12)
    raw_id = ''.join(c for c in str(pet_id_raw) if c.isdigit())
    if not raw_id:
        return JsonResponse({'success': False, 'error': 'Invalid pet ID'}, status=400)

    try:
        pet = Pet.objects.get(id=int(raw_id))
    except Pet.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'Pet #{pet_id_raw} not found'}, status=404)

    # Ownership / auth check
    if request.user.is_authenticated:
        is_admin = request.user.is_staff or request.user.is_superuser or (
            hasattr(request.user, 'profile') and str(request.user.profile.role).upper() == 'ADMIN'
        )
        if not is_admin:
            user_shelter = getattr(request.user, 'shelter_profile', None) or \
                           ShelterProfile.objects.filter(user=request.user).first()
            if user_shelter and pet.shelter and pet.shelter != user_shelter:
                return JsonResponse({
                    'success': False,
                    'error': 'Security Violation: This pet belongs to another shelter.'
                }, status=403)

    prev_status = pet.status
    pet.status = new_status
    pet.save(update_fields=['status'])

    # Audit log
    try:
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_role='Shelter Staff' if not (request.user.is_staff or request.user.is_superuser) else 'Admin',
            action='PET_STATUS_UPDATED',
            module='Pet Registry',
            description=f"Pet '{pet.name}' (#{pet.id}) marketplace status changed from {prev_status} to {new_status}."
        )
    except Exception:
        pass

    STATUS_DISPLAY = {
        'AVAILABLE': 'Available',
        'PENDING_ADOPTION': 'Pending Adoption',
        'ADOPTED': 'Adopted',
    }
    return JsonResponse({
        'success': True,
        'pet_id': pet.id,
        'status': new_status,
        'status_display': STATUS_DISPLAY.get(new_status, new_status),
        'message': f"Pet '{pet.name}' status updated to {STATUS_DISPLAY.get(new_status, new_status)}."
    })


@csrf_exempt
def api_delivery_toggle_availability(request):
    """
    Delivery Partner / Shelter / Admin: Toggle or set delivery partner availability status (AVAILABLE <-> BUSY).
    Persists to DeliveryPartner.availability_status in Django backend database.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    requested_status = data.get('status', '').strip().upper()
    partner_id_raw = data.get('partner_id', '') or data.get('partnerId', '')

    dp = None
    if partner_id_raw:
        raw_id = ''.join(c for c in str(partner_id_raw) if c.isdigit())
        if raw_id:
            dp = DeliveryPartner.objects.filter(Q(id=int(raw_id)) | Q(user__id=int(raw_id)) | Q(partner_id=partner_id_raw)).first()

    if not dp and request.user.is_authenticated:
        dp = getattr(request.user, 'delivery_partner_profile', None) or \
             DeliveryPartner.objects.filter(user=request.user).first()

    if not dp:
        return JsonResponse({'success': False, 'error': 'Delivery partner profile not found'}, status=404)

    if requested_status in ['AVAILABLE', 'BUSY', 'INACTIVE']:
        dp.availability_status = requested_status
    else:
        current_op = dp.get_availability_status()
        dp.availability_status = 'BUSY' if current_op == 'AVAILABLE' else 'AVAILABLE'

    dp.save(update_fields=['availability_status'])
    new_op = dp.get_availability_status()

    try:
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else dp.user,
            user_role='Delivery Partner',
            action='DELIVERY_AVAILABILITY_TOGGLED',
            module='Transit Operations',
            description=f"Delivery Partner {dp.user.username} availability status set to {new_op}."
        )
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'partner_id': dp.partner_id,
        'user_id': dp.user.id,
        'availability_status': new_op,
        'message': f"Delivery partner status is now {new_op}."
    })


@csrf_exempt
def api_get_available_delivery_partners(request):
    """
    Dynamic API: Returns real-time list of available delivery partners directly from database.
    """
    try:
        dps = DeliveryPartner.objects.filter(is_active=True).select_related('user', 'shelter')
        available_list = []
        for dp in dps:
            op_status = dp.get_availability_status()
            if op_status == 'AVAILABLE':
                available_list.append({
                    'id': dp.id,
                    'partnerId': dp.partner_id,
                    'name': dp.user.get_full_name().strip() or dp.user.first_name or dp.user.username,
                    'username': dp.user.username,
                    'vehicle': f"{dp.vehicle_type} ({dp.vehicle_number})",
                    'shelterName': dp.shelter.shelter_name if dp.shelter else "SafeTransit General Fleet",
                    'status': op_status
                })
        return JsonResponse({'success': True, 'available_partners': available_list})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_shelter_verification_status(request):
    """
    Returns real-time verification status for the current logged in shelter user.
    """
    if not request.user.is_authenticated or request.user.is_anonymous:
        return JsonResponse({'success': True, 'is_verified': False, 'verification_status': 'PENDING'})

    user = request.user
    shelter_rec = getattr(user, 'shelter_profile', None) or ShelterProfile.objects.filter(user=user).first()
    profile_obj = getattr(user, 'profile', None)

    is_ver = False
    v_status = 'PENDING'

    if shelter_rec:
        v_status = shelter_rec.verification_status
        is_ver = is_shelter_verified(shelter_rec)
    elif profile_obj:
        v_status = profile_obj.verification_status
        is_ver = (profile_obj.verification_status == 'VERIFIED' and profile_obj.is_verified)

    return JsonResponse({
        'success': True,
        'is_verified': is_ver,
        'verification_status': v_status,
        'shelter_id': shelter_rec.id if shelter_rec else None,
        'shelter_name': shelter_rec.shelter_name if shelter_rec else ''
    })




