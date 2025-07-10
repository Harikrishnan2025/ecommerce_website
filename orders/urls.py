from django.urls import path
from .views import  CreateOrderView,UserOrderListView,UserOrderDetailView,UserOrderCancelView,AdminOrderListView,UpdatrOrderStatusView

urlpatterns = [
    path('placeorder/', CreateOrderView.as_view(), name='placeorder'),
    path('vieworder/',UserOrderListView.as_view(),name='vieworder'),
    path('vieworder/<str:order_number>/',UserOrderDetailView.as_view(),name='single-order'),
    path('vieworder/<str:order_number>/delete/',UserOrderCancelView.as_view(),name='cancel-order'),
    path('adminlistview/',AdminOrderListView.as_view(),name='admin-listview'),
    path('adminlistview/update/<str:order_number>/',UpdatrOrderStatusView.as_view(),name='admi-order-update')


]
