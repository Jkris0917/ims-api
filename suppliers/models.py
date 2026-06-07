from django.db import models

# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
class SupplierProduct(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_products')
    products = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name='product_suppliers')
    supplier_sku = models.CharField(max_length=100, blank=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    lead_time_days = models.PositiveIntegerField(default=7)
    is_preferred = models.BooleanField(default=False)
    creared_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['supplier','product']
        
    def __str__(self):
        return f"{self.supplier.name} -> {self.product.name}"
    