from django.db import models
from django.contrib import settings

# Create your models here.
class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('completed','Completed'),
        ('cancelled','Cancelled'),
        ('refunded','Refunded'),
    ]
    
    reference = models.CharField(max_length=100, blank=True, null=True)
    customer_name = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True)
    sold_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True,related_name='sales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Sale {self.reference or self.id}"
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    def save(self, *args, **kwargs):
        if not self.reference:
            import uuid
            self.reference = f"SALE-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale,on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    @property
    def total_price(self):
        return (self.unit_price + self.quantity) * (1 - self.discount / 100)
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"