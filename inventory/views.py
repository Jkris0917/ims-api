from rest_framework import generics,filters,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import transaction
from django.utils import timezone
from .models import StockMovement,PurchaseOrder,PurchaseOrderItem
from .serializers import (StockAdjustmentSerializer,StockMovementSerializer,PurchaseOrderSerializer,PurchaseOrderCreateSerializer)
from products.views import IsAdminOrManager
from products.models import Product

# Create your views here.
class StockAdjustmentView(APIView):
    permission_classes = [IsAdminOrManager]
    
    @transaction.atomic
    def post(self, request):
        serializer = StockAdjustmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        product = data['product']
        quantity = data['quantity']
        
        new_stock = product.current_stock + quantity
        if new_stock < 0:
            return Response(
                {'detail': f'Insufficient stock. Current: {product.current_stock}, Requested: {abs(quantity)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        movement = StockMovement.objects.create(
            product=product,
            movement_type=data['movement_type'],
            quantity=quantity,
            quantity_before = product.current_stock,
            quantity_after = new_stock,
            unit_cost = data.get('unit_cost'),
            reference = data.get('reference',''),
            notes = data.get('notes',''),
            performed_by = request.user,
        )
        
        product.current_stock = new_stock
        product.save(update_fields=['current_stock'])
        
        return Response(
            StockMovementSerializer(movement).data,
            status=status.HTTP_201_CREATED
        )
        
class StockMovementListView(generics.ListAPIView):
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product_name','product_sku', 'reference']
    ordering_fields = ['created_at','quantity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = StockMovement.objects.select_related(
            'product', 'performed_by'
        )
        
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
            
        movement_type = self.request.query_params.get('movement_type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
            
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__date__gre=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
            
        return queryset
    
class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrManager]
    filter_backends = [filters.OrderingFilter]
    ordering = ['=created_at']
    
    def get_queryset(self):
        queryset = PurchaseOrder.objects.select_related(
            'supplier', 'created_by'
        ).prefetch_related('items__product')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer
    
    def perform_create(self,serializer):
        serializer.save(created_by=self.request.user)
        
class PurchaseOrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = PurchaseOrder.objects.select_related(
        'supplier','created_by'
    ).prefetch_related('items__product')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAdminOrManager]

class ReceivePurchaseOrderView(APIView):
    permission_classes = [IsAdminOrManager]
    
    @transaction.atomic
    def post(self,request,pk):
        try:
            po = PurchaseOrder.objects.select_related('supplier').prefetch_related(
                'items__product'
            ).get(pk=pk)
        except PurchaseOrder.DoesNotExist:
            return Response(
                {'detail':'Purchase order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        if po.status == 'received':
            return Response(
                {'detail':'Purchase order already received.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if po.status == 'cancelled':
            return Response(
                {'detail':'Cannot received a cancelled order.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        movements = []
        for item in po.items.all():
            product = item.product
            quantity = item.quantity_ordered
            
            movement = StockMovement(
                product=product,
                movement_type = 'purchase',
                quantity = quantity,
                quantity_before = product.current_stock,
                quantity_after = product.current_stock + quantity,
                unit_cost = item.unit_cost,
                reference = f'PO-{po.id:04d}',
                performed_by=request.user,
            )
            
            movements.append(movement)
        
            product.current_stock += quantity
            product.save(update_fields=['current_stock'])
        
            item.quantity_recieved = quantity
            item.save(update_fields=['quantity_received'])
    
        StockMovement.objects.bulk_create(movements)
        
        po.status = 'received'
        po.received_at = timezone.now()
        po.save(update_fields=['status','received_at'])
        
        return Response(
            {'detail': f'PO-{po.id:04d} received. {len(movements)} products restocked.'},
            status=status.HTTP_200_OK
        )
    