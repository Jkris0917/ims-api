from rest_framework import serializers
from .models import Alert

class AlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name',read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.full_name', read_only=True)
    
    class Meta:
        model = Alert
        fields = ['id','product','product_name','product_sku','alert_type','status','message','current_stock','minimum_stock','acknowledged_by','acknowledged_by_name','acknowledged_at','created_at']
        read_only_fields = [
            'id','product','alert_type','message','current_stock','minimum_stock','acknowledged_by','acknowledged_at','created_at'
        ]
    