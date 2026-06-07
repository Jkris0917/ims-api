from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Alert
from .serializers import AlertSerializer
from products.views import IsAdminOrManager

# Create your views here.
class AlertListView(generics.ListAPIView):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Alert.objects.select_related('product', 'acknowledged_by')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        alert_type = self.request.query_params.get('alert_type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
            
        return queryset
    
class AcknowledgeAlertView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
        except Alert.DoesNotExist:
            return Response(
                {'detail': 'Alert no found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if alert.status != 'active':
            return Response(
                {'detail': f'Alert is already {alert.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        alert.status = 'acknowledged'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save(update_fields=['status', 'acknowledged_by', 'acknowledged_at'])
        
        return Response(AlertSerializer(alert).data)
    
class ResolveAlertView(APIView):
    permission_classes = [IsAdminOrManager]
    
    def post(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
        except Alert.DoesNotExist:
            return Response(
                {'detail': 'Alert not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        alert.status = 'resolved'
        alert.save(update_fields=['status'])
        
        return Response(AlertSerializer(alert).data)

class CheckAndCreateAlertsView(APIView):
    permission_classes = [IsAdminOrManager]
    
    def post(self, request):
        from products.models import Product
        from django.db.models import F
        
        products = Product.objects.filter(is_active=True)
        created = 0
        
        for product in products:
            if product.current_stock == 0:
                alert_type = 'out_of_stock'
                message = f'{product.name} is out of stock.'
            elif product.current_stock <= product.minimum_stock:
                alert_type ='low_stock'
                message = (
                    f'{product.name} is running low.'
                    f'Current: {product.current_stock}'
                    f'Minimum: {product.minimum_stock}'
                )
            else:
                continue
            
            exists = Alert.objects.filter(
                product=product,
                alert_type = alert_type,
                status='active'
            ).exists()
            
            if not exists:
                Alert.objects.create(
                    product=product,
                    alert_type=alert_type,
                    message=message,
                    current_stock = product.current_stock,
                    minimum_stock = product.minimum_stock,
                )
                created += 1
        return Response({
            'detail': f'{created} new alerts created.',
            'total_checked': products.count(),
        })