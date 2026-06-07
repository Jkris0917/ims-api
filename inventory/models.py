from django.db import models
from django.contrib import settings

# Create your models here.
class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('purchase','Purchase'),
        ('sale','Sale'),
        ('adjustment','Adjustment'),
        ('return','Return'),
        ('damage','Damage'),
        ('transfer','Transfer'),
    ]
    
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference = models.CharField(max_length=200,blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True,related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        direction = '+' if self.quantity > 0 else ''
        return f"{self.product.name} {direction}{self.quantity} ({self.movement_type})"
    
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft','Draft'),
        ('ordered','Ordered'),
        ('received','Received'),
        ('cancelled','Cancelled'),
    ]
    
    suppliers = models.ForeignKey("suppliers.Supplier", on_delete=models.SET_NULL,null=True,related_name='purchase_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    ordered_at = models.DateTimeField(blank=True, null=True)
    received_at = models.DateTimeField(blank=True,null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,related_name='purchase_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PO-{self.id:04d} - {self.suppliers.name if self.supplier else 'No Supplier'}"
    
    @property
    def total_amount(self):
        return sum(item.total_cost for item in self.items.all())

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name='purchase_order_items')
    quantity_ordered = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total_cost(self):
        return self.quantity_ordered * self.unit_cost
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity_ordered}"