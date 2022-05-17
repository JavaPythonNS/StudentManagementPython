
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.core.exceptions import ValidationError
import random
import string
import datetime
from django.utils import timezone


def pincode_validation(data):
    if len(data)>6 or len(data)<6:
        raise ValidationError("Pincode must be 6 digits.")

def phone_validation(data):
    if len(data)> 10 or len(data)<10:
        raise ValidationError("Phone number must be 10 digits.")

def generate_reset_hash():
    return ''.join(random.choices(string.ascii_lowercase, k=25))

def expire_time():
    return timezone.now()+ timezone.timedelta(minutes=5)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, validators=[phone_validation])
    profile_image = models.FileField(upload_to='profile_images/', null=True, blank=True)
    house_number = models.CharField(max_length=10)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10, validators=[pincode_validation])
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELD = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

class ForgotPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hash = models.CharField(max_length=255, default=generate_reset_hash, null=True, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expire_at = models.DateTimeField(default=expire_time, null=True, blank=True)

    def __str__(self):
        return self.hash