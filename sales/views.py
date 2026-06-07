from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Sale, SaleItem
from .serializers import (SaleSerializer,SaleCreateSerializer,SaleListSerializer)
from products.views import IsAdminOrManager

# Create your views here.
class SaleListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference','customer_name','customer_email']
    ordering_fields = ['created_at','total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Sale.objects.prefetch_related(
            'items__product'
        ).select_related('sold_by')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        if not self.request.user.is_manager:
            queryset = queryset.filter(sold_by=self.request.user)
            
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SaleCreateSerializer
        return SaleListSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = SaleCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        
        if serializer.is_valid():
            sale = serializer.create(serializer.validated_data)
            return Response(
                SaleSerializer(sale).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SaleDetailView(generics.RetrieveAPIView):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Sale.objects.prefetch_related(
            'items__product'
        ).select_related('sold_by')
        
        if not self.request.user.is_manager:
            queryset = queryset.filter(sold_by=self.request.user)
        return queryset
    
class CancelSaleView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request,pk):
        try:
            sale=Sale.objects.prefetch_related(
                'items__product'
            ).get(pk=pk)
        except Sale.DoesNotExist:
            return Response(
                {'detail': 'Sale not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        if sale.status != 'completed':
            return Response(
                {'detail': f'Cannot cancel a {sale.status} sale.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from inventory.models import StockMovement
        
        for item in sale.items.all():
            product = item.product
            
            StockMovement.objects.create(
                product=product,
                movement_type='return',
                quantity = item.quantity,
                quantity_before = product.current_stock,
                quantity_after = product.current_stock + item.quantity,
                reference = f'CANCEL-{sale.reference}',
                performed_by = request.user
            )
            
            product.current_stock += item.quantity
            product.save(update_fields=['current_stock'])
            
        sale.status = 'cancelled',
        sale.save(update_fields=['status'])
        
        return Response(
            {'detail': f'Sale {sale.reference} cancelled. Stock restored.'},
            status=status.HTTP_200_OK
        )
        
class SalesSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Sum, Count
        from django.utils import timezone
        import datetime
        
        today = timezone.now().data()
        month_start = today.replace(day=1)
        
        queryset = Sale.objects.filter(status='completed')
        
        today_sales = queryset.filter(created_at__date=today)
        month_sales = queryset.filter(created_at__date__gte=month_start)
        
        return Response({
            'today':{
                'count': today_sales.count(),
                'total': today_sales.aggregate(
                    total=Sum('items__unit_price')
                )['total'] or 0,
            },
            'this_month':{
                'count':month_sales.count(),
                'total':month_sales.aggregate(
                    total=Sum('items__unit_price')
                )['total'] or 0,
            },
            'all_time':{
                'count': queryset.count(),
            },
        })
        
