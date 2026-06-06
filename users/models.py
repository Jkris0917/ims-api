from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin',"Admin"),
        ('manager',"Manager"),
        ('staff',"Staff"),
    ]
    
    fullname = models.CharField(max_length=255,blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return f"{self.full_name or self.username} - ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_manager(self):
        return self.role in ['admin','manager'] or self.is_superuser
    