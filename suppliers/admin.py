from django.contrib import admin
from .models import Supplier,SupplierProduct

# Register your models here.
class SupplierProductInLine(admin.ModelAdmin):
    model = SupplierProduct
    extra = 1
    fields = ('product','supplier_sku','unit_cost','lead_time_days','is_preferred')
    
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name','contact_person','email','phone','is_active','created_at')
    list_filter = ('is_active',)
    search_fields = ('name','contact_person','email')
    list_editable = ('is_active',)
    inlines = [SupplierProductInLine]
    
@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = ('supplier','product','unit_cost','lead_time_days','is_preferred')
    list_filter = ('is_preferred',)
    search_fields = ('supplier_name','product_name')