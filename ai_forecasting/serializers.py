from rest_framework import serializers
from .models import ForecastReport

class ForecastReportSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = ForecastReport
        fields = [
            'id','product','product_name','product_sku','current_stock','daily_sales_rate', 'days_until_stockout', 'recommended_reorder_quantity','ai_analysis','ai_recommendation','confidence_level','created_at',
        ]
        
        read_only_fields = fields