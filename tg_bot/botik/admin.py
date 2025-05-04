from django.contrib import admin
from .models import MyModel, Companie, Partner, Customer, Order

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'age')

@admin.register(Companie)
class CompaniesAdmin(admin.ModelAdmin):
    list_display = ('company', 'company_unique_id')

@admin.register(Partner)
class PartnersAdmin(admin.ModelAdmin):
    list_display = ('fio', 'company', 'email', 'password', 'logedIn', 'role')

@admin.register(Customer)
class CustomersAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'tg_name' ,'discount', 'orders_count')

@admin.register(Order)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_telegram_id', 'company', 'order_details', 'status')