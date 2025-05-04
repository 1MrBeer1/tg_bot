from rest_framework import serializers
from .models import MyModel, Companie, Partner, Customer, Order

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'

class CompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companie
        fields = '__all__'

class PartnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'

class CustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class OrdersSerializer(serializers.ModelSerializer):
    customer_telegram_id = CustomersSerializer()
    company = CompaniesSerializer()
    class Meta:
        model = Order
        fields = '__all__'