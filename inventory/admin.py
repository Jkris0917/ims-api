from django.contrib import admin
from .models import StockMovement, PurchaseOrder, PurchaseOrderItem

# Register your models here.
@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product','movement_type','quantity','quantity_before','quantity_after','performed_by','created_at')
    list_filter = ('movement_type',)
    search_fields = ('product__name','product__sku','reference')
    readonly_fields = ('product','movement_type','quantity','quantity_before','quantity_after','unit_cost','reference','notes','performed_by','created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj = None):
        return False
    
class PurchaseOrderItemInLine(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = (
        'product','quantity_ordered','quantity_received','unit_cost'
    )
    received_fields = ('quantity_received',)
    
@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id','supplier','status','total_amount','created_by','created_at')
    list_filter = ('status',)
    search_fields = ('supplier__name',)
    readonly_fields = ('created_by','created_at','updated_at','total_amount')
    inlines = [PurchaseOrderItemInLine]
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)