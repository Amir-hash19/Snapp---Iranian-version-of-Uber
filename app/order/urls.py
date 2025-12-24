from django.urls import path
from .views import OrderCreateView, OrderListView, OrderRetrieveView, OrderAcceptView, UserOrderRetrieveView



urlpatterns = [
    path("order/create/", OrderCreateView.as_view(), name="create-order"),
    path("orders/", OrderListView.as_view(), name="list-orders-for-driver"),
    path("order/<int:pk>/", OrderRetrieveView.as_view(), name="order-retrieve"),
    path("order/<int:pk>/accept/", OrderAcceptView.as_view(), name="order-accept-by-driver"),
    path("order/<int:pk>/status-accept/", UserOrderRetrieveView.as_view(), name="get-user-order-by-user")
]
