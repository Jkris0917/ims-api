from django.db import models
from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductListSerializer


class IsAdminOrManager(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.is_manager


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrManager]


class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'unit_price', 'current_stock', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = Product.objects.select_related('category')

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        stock_status = self.request.query_params.get('stock_status')
        if stock_status == 'low_stock':
            queryset = queryset.filter(
                current_stock__lte=models.F('minimum_stock')
            )
        elif stock_status == 'out_of_stock':
            queryset = queryset.filter(current_stock=0)

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrManager]

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.is_active = False
        product.save()
        return Response(
            {'detail': f'{product.name} deactivated successfully.'},
            status=status.HTTP_200_OK
        )


class LowStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        low_stock = Product.objects.filter(
            is_active=True,
            current_stock__lte=models.F('minimum_stock')
        ).select_related('category')
        serializer = ProductListSerializer(low_stock, many=True)
        return Response({
            'count': low_stock.count(),
            'products': serializer.data,
        })