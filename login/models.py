from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager



class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        (1, 'SuperAdmin'),
        (2, 'Admin'),
        (3, 'User'),
    )

    user_type = models.PositiveSmallIntegerField(
    choices=USER_TYPES,
    default=3
     ) 
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    verification_token = models.CharField(max_length=100, null=True, blank=True)
    
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)


    is_verified = models.BooleanField(default=False)


      
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
     

    objects = CustomUserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    

class cars(models.Model):
    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
        ('CNG', 'CNG'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    variant = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField(default=0)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='Petrol')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to='car_images/', null=True, blank=True)
    chassis_number = models.CharField(max_length=100, unique=True)
    insurance_number = models.CharField(max_length=100, unique=True)
    license_plate_number = models.CharField(max_length=100, unique=True)
    engine_number = models.CharField(max_length=100, unique=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

class CarImage(models.Model):
    car = models.ForeignKey(cars, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='car_images/')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.car.make} {self.car.model}"
