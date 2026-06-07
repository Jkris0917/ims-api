from django.db import models
from django.conf import settings

# Create your models here.
class Alert(models.Model):
    ALERT_TYPES = [
        ('low_stock','Low Stock'),
        ('out_of_stock','Out of Stock'),
        ('overstock','Overstock'),
        ('expiry','Expiry Warning'),
    ]
    
    STATUS_CHOICES = [
        ('active','Active'),
        ('acknowledged','Aknowledged'),
        ('resolved','Resolved'),
    ]
    
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    message = models.TextField()
    current_stock = models.PositiveIntegerField()
    minimum_stock = models.PositiveIntegerField()
    acknowledged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.alert_type} - {self.product.name}"