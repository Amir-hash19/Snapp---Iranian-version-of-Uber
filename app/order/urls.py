from django.urls import path
from .views import OrderCreateView, OrderListView



urlpatterns = [
    path("order/create/", OrderCreateView.as_view(), name="create-order"),
    path("orders/", OrderListView.as_view(), name="list-orders-for-driver")
]
