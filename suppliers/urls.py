from django.urls import path
from .views import SupplierDetailView,SupplierListCreateView,SupplierProductListCreateView,SupplierProductDetailView

urlpatterns = [
    #Suppliers
    path('suppliers/', SupplierListCreateView.as_view()),
    path('suppliers/<int:pk>', SupplierDetailView.as_view()),
    
    #Supplier Product
    path('suppliers/<int:supplier_id>/products/', SupplierProductListCreateView.as_view()),
    path('suppliers/<int:supplier_id>/producst/<int:pk>/', SupplierProductDetailView.as_view())
]
