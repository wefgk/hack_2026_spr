from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
import secrets

class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        
        email = self.normalize_email(email)
        
        if not name:
            raise ValueError('Имя обязательно')
        if not surname:
            raise ValueError('Фамилия обязательна')

        user = self.model(
            email=email,
            name=name,
            surname=surname,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    is_admin=models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    key = models.CharField(max_length=64, unique=True, editable=False)
    device_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.device_name or 'Device'} - {self.user.email}"