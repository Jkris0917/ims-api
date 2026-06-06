from rest_framework import serializers
from .models import Category,Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','description','product_count','created_at']
        read_only_fields = ['id','created_at']
        
    def get_product_count(self,obj):
        return obj.products.filter(is_active=True).count()

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    profit_margin = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id','category','category_name','name','sku','description','unit_price','cost_price','current_stock','minimum_stock','maximum_stock','unit','is_active','is_low_stock','stock_status','profit_margin','created_at','updated_at']
        read_only_fields = ['id','created_at','updated_at']
        
class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id','name','sku','category_name','unit_price','current_stock','minimin_stock','unit','stock_status','is_active',]
        