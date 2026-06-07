from rest_framework import serializers
from .models import Supplier,SupplierProduct

class SupplierProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
        
    class Meta:
        model = SupplierProduct
        fields = [
            'id','product','product_name','product_sku','supplier_sku','unit_cost','lead_time_days','is_preferred','created_at'
        ]
        read_only_fields = ['id','created_at']

class SupplierSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id','name','contact_person','email','phone','address','is_active','product_count','created_at','updated_at'
        ]
        read_only_fields = ['id','created_at','updated_at']
        
    def get_product_count(self,obj):
        return obj.suppliers_product.count()
    
class SupplierDetailSerializer(serializers.ModelSerializer):
    product = SupplierProductSerializer(source='supplier_products',many=True,read_only=True)
    
    class Meta(SupplierSerializer.Meta):
        fields = SupplierSerializer.Meta.fields + ['products']