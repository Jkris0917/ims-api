from rest_framework import serializers
from .models import DailySalesReport

class DailySalesReportSerializer(serializers.ModelSerializer):
    top_product_name = serializers.CharField(source='top_product.name',read_only=True)
    
    class Meta:
        model = DailySalesReport
        fields = [
            'id','date','total_sales','total_revenue','total_items_sold','top_product','top_product_name','created_at',
        ]
        
    