from django.urls import path
from .views import (DashboardStatsView,SalesTrendView,TopProductsView,StockValuationView)

urlpatterns = [
    path('analytics/dashboard/', DashboardStatsView.as_view()),
    path('analytics/sales-trend/', SalesTrendView.as_view()),
    path('analytics/top-products/', TopProductsView.as_view()),
    path('analytics/stock-valuation/', StockValuationView.as_view()),
]
