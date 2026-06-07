from django.contrib import admin
from .models import Sale,SaleItem

# Register your models here.
class SaleItemInLine(admin.TabularInline):
    model = SaleItem
    extra = 0
    fields = ('product','quantity', 'unit_price','discount','total_price')
    readonly_fields = ('total_price',)
    
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total'
    
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('reference', 'customer_name','status','total_amount','total_items','sold_by','created_at')
    list_filter = ('status',)
    search_fields = ('reference', 'customer_name','customer_email')
    readonly_fields = ('reference', 'sold_by', 'total_amount', 'total_items', 'created_at','updated_at')
    inlines = [SaleItemInLine]
    
    def has_delete_permission(self, request, obj = None):
        return False