from django.db import models
import hashlib

class MyModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    email = models.EmailField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    
#Сначала создаем компанию - она будет прикреплятся к пользователям (если удалить компанию - её пользователи пропадут)
class Companie(models.Model):
    company = models.CharField(max_length=150, null=True, blank=True)
    company_unique_id = models.PositiveBigIntegerField(unique=True)

    def __str__(self):
        return self.company
    
    #автоинкремент uniqie id
    def save(self, *args, **kwargs):
        if not self.pk:
            max_value = Companie.objects.aggregate(max_value=models.Max('company_unique_id'))['max_value']
            self.company_unique_id = (max_value or 0) + 1
        super().save(*args, **kwargs)

#Непосредственно пользователи для просмотра заказов, статы итд
class Partner(models.Model):
    fio = models.CharField(max_length=150, null=True, blank=True)
    company = models.ForeignKey(Companie, on_delete=models.CASCADE, related_name='partners')
    email = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=256)
    logedIn = models.BooleanField(default=False)
    role = models.CharField(max_length=15)

    def hash_data(self, data):
        if len(self.password) < 40:
            return hashlib.sha256(data.encode()).hexdigest()
        else:
            return self.password
    
    def save(self, *args, **kwargs):
        # Хешируем данные перед сохранением
        if self.password:
            self.password = self.hash_data(self.password)
        super().save(*args, **kwargs)

#Покупатели
class Customer(models.Model):
    telegram_id = models.CharField(max_length=40, unique=True)
    tg_name = models.CharField(max_length=150)
    discount = models.IntegerField(default=0)
    orders_count = models.BigIntegerField(default=-1)

    def save(self, *args, **kwargs):
        if not self.pk:
            max_value = Customer.objects.aggregate(max_value=models.Max('orders_count'))['max_value']
            self.orders_count = (max_value or -1) + 1
        super().save(*args, **kwargs)

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer_telegram_id = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='order_by_customer')
    company = models.ForeignKey(Companie, on_delete=models.CASCADE, related_name='orders')
    order_details = models.CharField(max_length=250)
    status = models.BooleanField(default=False)