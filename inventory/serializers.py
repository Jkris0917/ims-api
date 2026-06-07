from rest_framework import serializers
from django.utils import timezone
from .models import StockMovement, PurchaseOrder, PurchaseOrderItem
from products.serializers import ProductListSerializer

class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.full_name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id','product','product_name','product_sku','movement_type','quantity','quantity_before','quantity_after','unit_cost','reference','notes','performed_by','performed_by_name','created_at',
        ]
        read_only_fields = ['id','quantity_before','quantity_after','performed_by','created_at']
        
class StockAdjustmentSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=__import__('products.models', fromlist=['Product']).Product.objects.all()
    )
    
    quantity = serializers.IntegerField()
    movement_type = serializers.ChoiceField(choices=[
        ('purchase','Purchase'),
        ('adjustment','Adjustment'),
        ('return','Return'),
        ('damage','Damage'),
    ])
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2,required=False,allow_null=True)
    reference = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id','product', 'product_name','product_sku','quantity_ordered', 'quantity_received','unit_cost','total_cost',
        ]
        read_only_fields = ['id']
        
class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name',read_only=True)
    total_amount = serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'supplier', 'supplier_name', 'status',
            'notes', 'ordered_at', 'received_at',
            'created_by', 'created_by_name',
            'total_amount', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at'
        ]
        
class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['supplier','notes','items']
        
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order,
                **item_data
            )
        return purchase_order