from rest_framework import serializers
from django.db import transaction
from .models import Sale,SaleItem
from products.models import Product

class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = SaleItem
        fields = [
            'id','product','product_name','product_sku','quantity','unit_price','discount','total_price',
        ]
        read_only_fields = ['id']
        
class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    sold_by_name = serializers.CharField(source='sold_by.full_name',read_only=True)
    total_amount = serializers.DecimalField(max_digits=10,decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id','reference','customer_name','customer_email','status','notes','sold_by','sold_by_name','total_amount','total_items','items','created_at','updated_at'
        ]
        read_only_fields =['id','reference','sold_by','created_at','updated_at']

class SaleCreateSerializer(serializers.Serializer):
    customer_name = serializers.CharField(required=False, allow_blank=True)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(child=serializers.DictField(), min_length=1)
    
    def validate_items(self, items):
        validated_items = []
        for item in items:
            product_id = item.get('product')
            quantity = item.get('quantity')
            
            if not product_id or not quantity:
                raise serializers.ValidationError(
                    'Each item requires product and quantity.'
                )
            try:
                product = Product.objects.get(pk=product_id,is_active=True)
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f'Product {product_id} not found or inactive.'
                )
                
            if product.current_stock < quantity:
                raise serializers.ValidationError(
                    f'Insufficient stock for {product.name}.',
                    f'Available: {product.current_stock}, Requested: {quantity}'
                )
            validated_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': item.get('unit_price', product.unit_price),
                'discount': item.get('discount', 0),
            })
            
        return validated_items
    
    @transaction.atomic
    def create(self, validated_data):
        from inventory.models import StockMovement
        
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        sale = Sale.objects.create(sold_by=user, **validated_data)
        
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price = item_data['unit_price'],
                discount = item_data['discount'],
            )
            
            StockMovement.objects.create(
                product=product,
                movement_type ='sale',
                quantity=-quantity,
                quantity_before = product.current_stock,
                quantity_after = product.current_stock - quantity,
                reference =sale.reference,
                performed_by = user
            )
            
            product.current_stock -= quantity
            product.save(update_fields=['current_stock'])
        
        return sale
    
class SaleListSerializer(serializers.ModelSerializer):
    sold_by_name = serializers.CharField(source='sold_by.full_name', read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'reference', 'customer_name',
            'status', 'sold_by_name', 'total_amount',
            'total_items', 'created_at',
        ]