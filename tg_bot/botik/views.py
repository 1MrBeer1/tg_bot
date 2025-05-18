import hashlib
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MyModel, Companie, Partner, Customer, Order
from .serializers import MyModelSerializer, CompaniesSerializer, PartnersSerializer, CustomersSerializer, \
    OrdersSerializer
from django.core.exceptions import ObjectDoesNotExist
from .serializers import OrdersSerializer


class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer


class CompanieViewSet(viewsets.ModelViewSet):
    queryset = Companie.objects.all()
    serializer_class = CompaniesSerializer


class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnersSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomersSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer


@api_view(['POST'])
def recieve_data(request):
    # message = request.data.get('message', 'No message provided')
    # text = request.data.get('text', 'No text provided')
    # print(message, text)
    # companie_instance = Companie.objects.get(company_unique_id=1)
    # new_Partner = Partner(
    #     fio='Трегубов Алексей Сергеевич',
    #     company= companie_instance,
    #     email='somexoticboy@yandex.ru',
    #     password='PxRtyfgh9831'
    # )
    # new_Partner.save()
    return Response({"received_message": "хых"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_logIn(request):
    gotEmail = request.data.get('email')
    psw = request.data.get('pass')
    hashed = hashlib.sha256(psw.encode()).hexdigest()
    try:
        obj = Partner.objects.get(email=gotEmail)
        print(hashed)
        print(obj.password)
        if (gotEmail == obj.email and hashed == obj.password):
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def isLoggedIn(request):
    gotEmail = request.data.get('email')
    try:
        obj = Partner.objects.get(email=gotEmail)
        if (gotEmail == obj.email):
            if (obj.logedIn == True):
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def setLogIn(request):
    newStatus = request.data.get("status")
    gotEmail = request.data.get("email")
    try:
        partner_instance = Partner.objects.get(email=gotEmail)
        partner_instance.logedIn = newStatus
        partner_instance.save()
        return Response({"company_id": partner_instance.company.company_unique_id}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)


@api_view(['POST'])
def checkUser(request):
    id = request.data.get("telId")
    try:
        user = Customer.objects.get(telegram_id=id)
        return Response(status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        new_customer = Customer(telegram_id=id)
        new_customer.save()
        return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
def makeOrder(request):
    teleg_id = request.data.get("tg_id")
    company_id = request.data.get("company")
    order = request.data.get("order")
    try:
        client_instance = Customer.objects.get(telegram_id=teleg_id)
        company_instance = Companie.objects.get(company_unique_id=company_id)
        new_order = Order(
            customer_telegram_id=client_instance,
            company=company_instance,
            order_details=order
        )
        new_order.save()
        return Response(status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        print("Error with adding order")
        return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)


@api_view(['POST'])
def getOrdersToDo(request):
    company_id = request.data.get("company")
    try:
        company_instance = Companie.objects.get(company_unique_id=company_id)
        answ = company_instance.orders.filter(status=False)
        orders_data = OrdersSerializer(answ, many=True)
        return Response({"orders": orders_data.data}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def orderComplete(request):
    order_id = request.data.get('order_id')
    try:
        order_instance = Order.objects.get(order_id=order_id)
        order_instance.status = True
        order_instance.save()
        return Response(status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_204_NO_CONTENT)
@api_view(['GET'])
def get_last_order(request):
    tg_id = request.GET.get('tg_id')
    try:
        customer = Customer.objects.get(telegram_id=tg_id)
        last_order = Order.objects.filter(customer_telegram_id=customer).latest('order_id')
        return Response({'order': last_order.order_details}, status=status.HTTP_200_OK)
    except (Customer.DoesNotExist, Order.DoesNotExist):
        return Response({}, status=status.HTTP_200_OK)