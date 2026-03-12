from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from core.models import BaseModel
import os

def user_profile_path(instance, filename):
    return f'profiles/user_{instance.id}/filename'
# Create your models here.
#custom user manager
class CustomeUserManger(BaseUserManager):
    def create_user(self, email, first_name, last_name, password = None, **extra_fields):
        if not email:
            raise ValueError('The Email is required.')
        
        email = self.normalize_email(email)
        user = self.model(
            email = email,
            first_name = first_name, 
            last_name = last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, password = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, first_name, last_name, password, **extra_fields)


# custom user model 
class User(AbstractUser, BaseModel):
    username = None
    email = models.EmailField(verbose_name= 'Email Address', unique=True)
    first_name = models.CharField( verbose_name='First Name', max_length= 50)
    last_name = models.CharField(verbose_name= 'Last Name', max_length=150)
    is_librarian = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_path,
        null=True,
        blank=True
    )
    objects = CustomeUserManger()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        # Cleanly handles name or fallback to email
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name if full_name else self.email



