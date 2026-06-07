from django.urls import path
from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    LowStockView,
    ProductDetailView,
    ProductListCreateView
)

urlpatterns = [
    #Categories
    path('categories/', CategoryListCreateView.as_view()),
    path('categories/<int:pk>', CategoryDetailView.as_view()),
    
    #Products
    path('products/', ProductListCreateView.as_view()),
    path('products/<int:pk>/',ProductDetailView.as_view()),
    path('products/low-stock/', LowStockView.as_view()),
]
