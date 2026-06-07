from rest_framework import generics,filters,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Supplier,SupplierProduct
from .serializers import (SupplierDetailSerializer,SupplierProductSerializer,SupplierSerializer)
from products.views import IsAdminOrManager

# Create your views here.
class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name','contact_person','email']
    ordering_fields = ['name','created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = Supplier.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    permission_classes = [IsAdminOrManager]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SupplierDetailSerializer
        return SupplierSerializer
    
class SupplierProductListCreateView(generics.ListCreateAPIView):
    serializer_class = SupplierProductSerializer
    permission_classes = [IsAdminOrManager]
    
    def get_queryset(self):
        return SupplierProduct.objects.filter(
            supplier_id = self.kwargs['supplier_id']
        ).select_related('product')
        
    def perform_create(self, serializer):
        supplier = Supplier.objects.get(pk=self.kwargs['supplier_id'])
        serializer.save(supplier=supplier)
        
class SupplierProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SupplierProductSerializer
    permission_classes = [IsAdminOrManager]
    
    def get_queryset(self):
        return SupplierProduct.objects.filter(
            supplier_id=self.kwargs['supplier_id']
        )