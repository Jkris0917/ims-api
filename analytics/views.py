from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum,Count,Avg,F
from django.utils import timezone
from datetime import timedelta
from .models import DailySalesReport
from .serializers import DailySalesReportSerializer
from sales.models import Sale, SaleItem
from products.models import Product
from inventory.models import StockMovement

# Create your views here.
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        month_start = today.replace(day=1)
        week_start = today - timedelta(days=7)
        
        completed_sales = Sale.objects.filter(status='completed')
        
        today_sales = completed_sales.filter(created_at__date=today)
        today_revenue = SaleItem.objects.filter(sale__in=today_sales).aggregate(total=Sum(F('unit_price') * F('quantity')))['total'] or 0
        
        month_sales = completed_sales.filter(created_at__date__gte=month_start)
        month_revenue = SaleItem.objects.filter(sale__in=month_sales).aggregate(total=Sum(F('unit_price') * F('quantity')))['total'] or 0
        
        total_products = Product.objects.filter(is_active=True).count()
        low_stock_count = Product.objects.filter(is_active=True,current_stock__lte=F('minimum_stock')).count()
        
        out_of_stock_count = Product.objects.filter(is_active=True,current_stock=0).count()
        
        top_products = SaleItem.objects.filter(
            sale__in=month_sales
        ).values(
            'product__id','product__name','product__sku'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('unit_price') * F('quantity'))
        ).order_by('-total_quantity')[:5]
        
        recent_movements = StockMovement.objects.select_related(
            'product','performed_by'
        ).order_by('-created_at')[:10]
        
        from inventory.serializers import StockMovementSerializer
        
        return Response({
            'today': {
                'sales_count': today_sales.count(),
                'revenue': today_revenue,
            },
            'this_month': {
                'sales_count': month_sales.count(),
                'revenue': month_revenue,
            },
            'inventory':{
                'total_products': total_products,
                'low_stock_products': low_stock_count,
                'out_of_stock_count': out_of_stock_count,
            },
            'top_products': list(top_products),
            'recent_movements': StockMovementSerializer(recent_movements, many=True).data,
        })
        
class SalesTrendView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        daily_data = Sale.objects.filter(
            status='completed',
            created_at__date__range=[start_date, end_date]
        ).values('created_at__date').annotate(
            sales_count=Count('id'),
            revenue=Sum('items__unit_price')
        ).order_by('created_at__date')
        
        return Response({
            'date': days,
            'start_date':start_date,
            'end_date': end_date,
            'data': list(daily_data),
        })
        
class TopProductsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        limit = int(request.query_params.get('limit',10))
        order_by = request.query_params.get('order_by','quantity')
        
        top_products = SaleItem.objects.filter(
            sales__status='completed'
        ).values(
            'product__id',
            'product__name',
            'product__sku',
            'product__current_stock',
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('unit_price') * F('quantity')),
        )
        
        if order_by == 'revenue':
            top_products = top_products.order_by('-total_revenue')
        else:
            top_products = top_products.order_by('-total_quantity')
        
        return Response(list(top_products[:limit]))
    
class StockValuationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import ExpressionWrapper,DecimalField
        
        products = Product.objects.filter(is_active=True).annotate(
            stock_value=ExpressionWrapper(
                F('current_stock') * F('cost_price'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
        
        total_value = products.aggregate(
            total=Sum('stock_value')
        )['total'] or 0
        
        category_breakdown = products.values(
            'category__name'
        ).annotate(
            total_value=Sum(
                ExpressionWrapper(
                    F('current_stock') * F('cost_price'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            ),
            product_count=Count('id')
        ).order_by('-total_value')
        
        return Response({
            'total_inventory_value': total_value,
            'by_category': list(category_breakdown),
        })