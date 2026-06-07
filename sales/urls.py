from django.urls import path
from .views import (SaleListCreateView,SaleDetailView,CancelSaleView,SalesSummaryView)

urlpatterns = [
    path('sales/', SaleListCreateView.as_view()),
    path('sales/summary/', SalesSummaryView.as_view()),
    path('sales/<int:pk>/', SaleDetailView.as_view()),
    path('sales/<int:pk>/cancel/', CancelSaleView.as_view()),
]
