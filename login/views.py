import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout as auth_logout, update_session_auth_hash
import requests
from django.conf import settings
from .forms import CarPredictionForm, UserForm, CarForm, updateprofileform
from .models import CarImage, User, cars
from django.contrib import messages
import random
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import User, cars
import pickle
import numpy as np


def _send_otp_email(to_email, otp):
    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        },
        json={
            "sender": {
                "name": settings.BREVO_SENDER_NAME,
                "email": settings.BREVO_SENDER_EMAIL
            },
            "to": [{"email": to_email}],
            "subject": "Your Fairy Club Verification Code",
            "textContent": f"Your OTP is: {otp}\n\nThis code expires in 5 minutes.",
        }
    )
    print("Brevo response:", response.status_code, response.text)





def members(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = UserForm()
    return render(request, 'signup.html', {'form': form})

def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone_number')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.', extra_tags='error')
                return render(request, 'signup.html', {'form': form})

            elif phone and User.objects.filter(phone_number=phone).exists():
                messages.error(request, 'Phone number already exists.', extra_tags='error')
                return render(request, 'signup.html', {'form': form})
            elif phone and len(phone) < 10:
                messages.error(request, 'Phone number must be at least 10 digits.', extra_tags='error')
                return render(request, 'signup.html', {'form': form})
            elif phone and not phone.isdigit():
                messages.error(request, 'Phone number must contain only digits.', extra_tags='error')
                return render(request, 'signup.html', {'form': form})

            otp = str(random.randint(100000, 999999))

            print(f"\n[DEV] OTP for {email}: {otp}\n")
            try:
                _send_otp_email(email, otp)
            except Exception as e:
                print(f"[ERROR] Failed to send OTP email: {e}")
                messages.error(request, 'Failed to send OTP email. Please try again.', extra_tags='error')
                return render(request, 'signup.html', {'form': form})

            request.session['pending_user'] = {
                'username': form.cleaned_data.get('username'),
                'email': email,
                'phone_number': phone,
                'password': form.cleaned_data['password'],
                'otp': otp,
            }
            request.session['verify_email'] = email
            request.session.save()
            return redirect('verify_otp')

    else:
        form = UserForm()

    return render(request, 'signup.html', {'form': form})

def home(request):
    featured_cars = cars.objects.filter(is_approved=True).order_by('-created_at')[:6]
    makes = cars.objects.filter(is_approved=True).values_list('make', flat=True).distinct()
    years = cars.objects.filter(is_approved=True).values_list('year', flat=True).distinct().order_by('-year')
    total_listings = cars.objects.filter(is_approved=True).count()
    selected_make = request.GET.get('make', '')
    models_for_make = (
        cars.objects.filter(is_approved=True, make=selected_make)
        .values_list('model', flat=True).distinct()
        if selected_make else []
    )
    return render(request, 'home.html', {
        'featured_cars': featured_cars,
        'makes': makes,
        'years': years,
        'total_listings': total_listings,
        'models_for_make': models_for_make,
        'selected_make': selected_make,
    })

def listings(request):
    
    fuel_type = request.GET.get('fuel_type')

    cars_list = cars.objects.filter(is_approved=True).order_by('-created_at')

    if fuel_type:
        cars_list = cars_list.filter(fuel_type__iexact=fuel_type)  

    return render(request, 'listings.html', {'cars': cars_list})
    

    
@login_required(login_url='login')
def sell(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.owner = request.user
            car.save()

            images = request.FILES.getlist('images')
            for i, img in enumerate(images):
                CarImage.objects.create(
                    car=car,
                    image=img,
                    is_main=(i == int(request.POST.get('main_image_index', 0)))
                )

            messages.success(request, 'Car listed successfully!')
            return redirect('dashboard')
        return render(request, 'sell.html', {'form': form})
    form = CarForm()
    return render(request, 'sell.html', {'form': form})

def financing(request):
    return render(request, 'financing.html')

def about(request):
    return render(request, 'about.html')



@login_required
def dashboard(request):
    
    if request.user.user_type == 1 or request.user.is_superuser:
       
        all_users = User.objects.filter(user_type=3).order_by('-id')
        
        
        all_cars = cars.objects.all().order_by('-created_at')
        
       
        stats = {
            'total_users': all_users.count(),
            'total_listings': all_cars.count(),
            'pending_approvals': cars.objects.filter(is_approved=False).count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
        }

        context = {
            'is_superadmin': True,
            'user_cars': all_cars,
            'all_users': all_users,
            'stats': stats,
        }
    else:
        
        user_cars = cars.objects.filter(owner=request.user).order_by('-created_at')
        
        context = {
            'is_superadmin': False,
            'user_cars': user_cars,
        }

    return render(request, 'dashboard.html', context)


def edit_car(request, pk):
    
    if request.user.user_type == 1:
        car = cars.objects.get(pk=pk)
    else:
        car = cars.objects.get(pk=pk, owner=request.user)

    existing_images = car.images.all()

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()

            delete_ids = request.POST.getlist('delete_images')
            if delete_ids:
                CarImage.objects.filter(id__in=delete_ids, car=car).delete()

            new_images = request.FILES.getlist('images')
            main_index = int(request.POST.get('main_image_index', 0))

            for i, img in enumerate(new_images):
                CarImage.objects.create(
                    car=car,
                    image=img,
                    is_main=(i == main_index)
                )

            messages.success(request, 'Car updated successfully!')
            return redirect('dashboard')

        
        return render(request, 'sell.html', {
            'form': form,
            'car': car,
            'existing_images': car.images.all(),
        })

    
    form = CarForm(instance=car)
    return render(request, 'sell.html', {
        'form': form,
        'car': car,
        'existing_images': existing_images,
    })

def delete_car(request, pk):
    if request.user.user_type == 1:
        car = cars.objects.get(pk=pk)
    else:
        car = cars.objects.get(pk=pk, owner=request.user)
    car.delete()
    messages.success(request, 'Car deleted successfully.')
    return redirect('dashboard')

@login_required
def approve_car(request, pk):
    if request.user.user_type != 1:
        return redirect('dashboard')
    car = cars.objects.get(pk=pk)
    car.is_approved = not car.is_approved
    car.save()
    status = 'approved' if car.is_approved else 'unapproved'
    messages.success(request, f'Car {status} successfully.')
    return redirect('dashboard')

@login_required
def ban_user(request, pk):
    if request.user.user_type != 1:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return redirect('dashboard')
    
    
    target = User.objects.get(pk=pk)
    target.is_active = not target.is_active
    target.save()
    action = 'unbanned' if target.is_active else 'banned'
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_active': target.is_active,
            'message': f'User {action} successfully.'
        })

    messages.success(request, f'User {action} successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def delete_user(request, pk):
    if request.user.user_type != 1:
        return redirect('dashboard')
    target = User.objects.get(pk=pk)
    target.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('dashboard')

@login_required
def edit_user(request, pk):
    if request.user.user_type != 1:
        return redirect('dashboard')
        
    target = User.objects.get(pk=pk)
    
    if request.method == 'POST':
        # Update existing fields
        target.name = request.POST.get('name', target.name)
        target.user_type = int(request.POST.get('user_type', target.user_type))
        target.is_verified = request.POST.get('is_verified') == 'on'
        target.is_active = request.POST.get('is_active') == 'on'
        
        # --- ADD THE NEW FIELDS HERE ---
        target.first_name = request.POST.get('first_name', target.first_name)
        target.last_name = request.POST.get('last_name', target.last_name)
        target.username = request.POST.get('username', target.username)
        target.age = request.POST.get('age') or None # Handles empty string
        target.phone_number = request.POST.get('phone_number') or None
        
        # Handle Profile Picture
        if 'profile_picture' in request.FILES:
            target.profile_picture = request.FILES['profile_picture']
            
        target.save()
        messages.success(request, 'User updated successfully.')
        return redirect('dashboard')
        
    return render(request, 'edit_user.html', {'target': target})

def update_profile(request):
    if request.method == 'POST':
        form = updateprofileform(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('dashboard')
        else:
            
            messages.error(request, 'Please correct the errors below.')
    else:
        form = updateprofileform(instance=request.user)

    return render(request, 'update_profile.html', {'form': form})

    
    return render(request, 'update_profile.html', {'form': form})
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
          
        user = User.objects.filter(email=email).first()
        
        if not user:
            print(f"[DEV] Login failed: no user found with email={email}")
            messages.error(request, 'Invalid email or password.')
        elif not user.check_password(password):
            print(f"[DEV] Login failed: wrong password for email={email}")
            messages.error(request, 'Invalid email or password.')
        # elif user.user_type == 1:
        #         login(request, user)
        #         return redirect('/admin/')
        elif not user.is_verified:
            print(f"[DEV] Login failed: user not verified email={email}")
            messages.error(request, 'Account verification has been removed contact admin.')
        elif not user.is_active:
            print(f"[DEV] Login failed: user is inactive email={email}")
            messages.error(request, 'Your account has been banned. Contact support for help.')
        else:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('home')
  
    return render(request, 'login.html')

def user_logout(request):
    auth_logout(request)
    return redirect('home')

def search(request):
    return render(request, 'search.html')

def car_detail(request, pk):
    car = cars.objects.filter(pk=pk, is_approved=True).first() 
    similar_cars = cars.objects.filter(make=car.make, is_approved=True).exclude(pk=pk)[:4]
    return render(request, 'car_detail.html', {'pk': pk, 'car': car, 'similar_cars': similar_cars})






def contact(request):
    return render(request, 'contact.html')

def privacy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')



@csrf_exempt
def resend_otp(request):
    if request.method == 'POST':
        email = request.session.get('verify_email')
        pending = request.session.get('pending_user')
        if not email or not pending:
            messages.error(request, 'Session expired. Please signup again.')
            return redirect('signup')

        new_otp = str(random.randint(100000, 999999))
        pending['otp'] = new_otp
        request.session['pending_user'] = pending  

        _send_otp_email(email, new_otp)
        messages.success(request, 'A new OTP has been sent to your email.')
    return redirect('verify_otp')

@csrf_exempt
def verify_otp(request):
    if request.user.is_authenticated:
        return redirect('home')
    email = request.session.get('verify_email')
    pending = request.session.get('pending_user')

    if not email or not pending:
        # Guard against double-submit race: if account was just created, send to login
        if email and User.objects.filter(email=email, is_verified=True).exists():
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
        messages.error(request, 'Session expired. Please signup again.')
        return redirect('signup')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == pending['otp']:
           
            user = User(
                username=pending.get('username'),
                email=pending['email'],
                phone_number=pending.get('phone_number') or None,
                is_verified=True,
            )
            user.set_password(pending['password'])
            user.save()

            del request.session['pending_user']
            del request.session['verify_email']

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('home')

        messages.error(request, 'Invalid OTP.')

    return render(request, 'verify_otp.html')

with open(os.path.join(os.path.dirname(__file__), 'car_price_model_v2.pkl'), 'rb') as f:
    model_data = pickle.load(f)

w = model_data['w']
b = model_data['b']
X_mean = model_data['X_mean']
X_std = model_data['X_std']
y_mean = model_data['y_mean']
y_std = model_data['y_std']

def predict_price(request):
    estimated_price = None
    form = CarPredictionForm()

    if request.method == 'POST':
        form = CarPredictionForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data

            car_age = 2025 - d['year']
            age_squared = car_age ** 2
            kms_per_age = d['kms_driven'] / car_age

            features = np.array([[
                car_age,
                d['kms_driven'],
                int(d['seller_type']),
                int(d['fuel_type']),
                int(d['transmission']),
                d['max_power'],
                age_squared,
                kms_per_age
            ]])

            features_scaled = (features - X_mean) / X_std
            price_scaled = np.dot(features_scaled, w).item() + b
            estimated_price = round(float((price_scaled * y_std) + y_mean), 2)

            if estimated_price < 0:
                estimated_price = 0.0

    return render(request, 'predict.html', {
        'form': form,
        'estimated_price': estimated_price,
        'prediction_made': estimated_price is not None,
    })