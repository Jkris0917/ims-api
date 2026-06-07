from django.urls import path
from .views import (
    StockAdjustmentView,
    StockMovementListView,
    PurchaseOrderListCreateView,
    PurchaseOrderDetailView,
    ReceivePurchaseOrderView,
)

urlpatterns = [
    
    #Stock Movements
    path('inventory/adjust/', StockAdjustmentView.as_view()),
    path('inventory/movements/', StockMovementListView.as_view()),
    
    #Purchase Orders
    path('inventory/purchase-orders/', PurchaseOrderListCreateView.as_view()),
    path('inventory/purchase-orders/<int:pk>/', PurchaseOrderDetailView.as_view()),
    path('inventory/purchase-orders/<int:pk>/receive/', ReceivePurchaseOrderView.as_view()),
]
