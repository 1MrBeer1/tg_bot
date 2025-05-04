from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'mymodel', MyModelViewSet)
router.register(r'companie', CompanieViewSet)
router.register(r'partner', PartnerViewSet)
router.register(r'customer', CustomerViewSet)
router.register(r'order', OrderViewSet)

urlpatterns = [
    path('data', recieve_data),
    path('validate/check/logIn', check_logIn),#authorization
    path('validate/check/setLogIn', setLogIn),#setLogInForCheck
    path("validate/check/isLoggedIn", isLoggedIn),#isLoggedIn?
    path('validate/check/checkUser', checkUser),#teleg check
    path('makeOrder', makeOrder),#make Order
    path('getOrders', getOrdersToDo),#get orders to do
    path('orderComplete', orderComplete),
    path('', include(router.urls))
]