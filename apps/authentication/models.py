# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
from simple_history.models import HistoricalRecords


# ===============================
#  USER MANAGEMENT
# ===============================

# User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, username, phone, password=None):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")
        if not phone:
            raise ValueError("Phone number is required")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phone=phone
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone, password=None):
        user = self.create_user(email, username, phone, password)
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


# Role Model
class Role(models.Model):
    ROLE_CATEGORIES = [
        ("admin", "Admin"),
        ("client", "Client"),
        ("manager", "Manager"),
        ("chef", "Chef"),
        ("waiter", "Waiter"),
        ("customer", "Customer"),
    ]

    role_name = models.CharField(max_length=100, unique=True)
    role_category = models.CharField(max_length=100, choices=ROLE_CATEGORIES, default="customer")
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.role_name

    class Meta:
        db_table = 'role'


# User Model
class Users(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(max_length=100, blank=True, null=True, unique=True)
    username = models.CharField(max_length=100, unique=True, blank=False, null=False)
    profile_image = models.TextField(blank=True, null=True)
    firebase_id = models.TextField(blank=True, null=True, default=None)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    address = models.TextField(blank=True, null=True, default=None)
    otp = models.IntegerField(blank=True, null=True, default=None)

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "phone"]

    objects = UserManager()
    history = HistoricalRecords()

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'


# User Role Assignment (Many-to-Many)
class UserRole(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_users")
    created_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, related_name="created_roles")
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user.username} - {self.role.role_name}"

    class Meta:
        db_table = 'user_role'
        unique_together = ("user", "role")


# ===============================
#  RESTAURANT & SUBSCRIPTION SYSTEM
# ===============================

# Restaurant Model
class Restaurant(models.Model):
    owner = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "restaurant"


# Subscription Plan (Defines pricing & duration)
class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    name = models.CharField(max_length=100, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=365)  # 1 year by default
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

    class Meta:
        db_table = "subscription_plan"


# Restaurant Subscription (Tracks each restaurant’s active plan)
class RestaurantSubscription(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    payment_reference = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # Auto set end date based on plan duration
        if not self.end_date and self.plan:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        # Auto deactivate if expired
        if self.end_date and self.end_date < timezone.now():
            self.is_active = False
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.end_date and timezone.now() > self.end_date

    def __str__(self):
        return f"{self.restaurant.name} - {self.plan.name if self.plan else 'No Plan'}"

    class Meta:
        db_table = "restaurant_subscription"


# Payment History
class PaymentTransaction(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=200, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50, choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending')
    ], default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.restaurant.name} - {self.transaction_id}"

    class Meta:
        db_table = "payment_transaction"
