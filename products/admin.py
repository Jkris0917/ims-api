from django.contrib import admin
from .models import Category,Product

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name')
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','sku','category','unit_price', 'current_stock','minimum_stock','stock_status','is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'sku', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'stock_status', 'profit_margin')
    
    fieldsets = (
        ('Basic Info',{
            'fields': ('name','sku','category','description','unit','is_active')
        }),
        ('Pricing',{
            'fields': ('unit_price','cost_price','profit_margin')
        }),
        ('Stock', {
            'fields': ('current_stock', 'minimum_stock','maximum_stock','stock_status')
        }),
        ('Timestamps',{
            'fields': ('created_at','updated_at')
        })
    )
