from django.urls import path
from .views import (
    AlertListView,
    AcknowledgeAlertView,
    ResolveAlertView,
    CheckAndCreateAlertsView,
)

urlpatterns = [
    path('alerts/', AlertListView.as_view()),
    path('alerts/check/', CheckAndCreateAlertsView.as_view()),
    path('alerts/<int:pk>/acknowledge/', AcknowledgeAlertView.as_view()),
    path('alerts/<int:pk>/resolve/', ResolveAlertView.as_view()),
]