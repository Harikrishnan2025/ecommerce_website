from django.urls import path
from .views import  CreateOrderView,UserOrderListView,UserOrderDetailView,UserOrderCancelView,AdminOrderListView,UpdatrOrderStatusView

urlpatterns = [
    path('placeorder/', CreateOrderView.as_view(), name='placeorder'),
    path('vieworder/',UserOrderListView.as_view(),name='vieworder'),
    path('vieworder/<str:order_number>/',UserOrderDetailView.as_view(),name='single-order'),
    path('cancelorder/<str:order_number>/',UserOrderCancelView.as_view(),name='cancel-order'),
    path('adminlistview/',AdminOrderListView.as_view(),name='admi-listview'),
    path('updatestatus/<str:order_number>/',UpdatrOrderStatusView.as_view(),name='admi-order-update')


]
