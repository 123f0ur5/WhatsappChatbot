from django.db import models

# Create your models here.
class Contacts(models.Model):
    name = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=16, unique=True)
    class Meta: verbose_name_plural = 'Contacts'

    def get_absolute_url(self):
        return f"/chat/{self.id}"
    def __str__(self):
        return self.name

class Messages(models.Model):
    from_number = models.CharField(max_length=16)
    to_number = models.CharField(max_length=16)
    message_text = models.TextField()
    sent_datetime = models.DateTimeField()
    contact_id = models.ForeignKey(
        Contacts,
        on_delete=models.CASCADE
    )
    class Meta: verbose_name_plural = 'Messages'

class Categories(models.Model):
    name = models.CharField(max_length=80)
    class Meta: verbose_name_plural = 'Categories'
    def __str__(self):
        return self.name

class Products(models.Model):
    name = models.CharField(max_length=80)
    price = models.FloatField()
    image = models.ImageField(blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Categories,
        on_delete=models.CASCADE
    )
    class Meta: verbose_name_plural = 'Prodcuts'
    def __str__(self):
        return self.name

class Orders(models.Model):
    contact_id = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    total_value = models.FloatField(blank=True)
    order_date = models.DateTimeField(blank=True, null=True)
    deliver_address = models.TextField(blank=True)
    status = models.CharField(max_length=12, blank=True)
    observation = models.CharField(max_length=250, blank=True)

    def get_absolute_url(self):
        return f"/manage/{self.id}"

    class Meta: verbose_name_plural = 'Orders'

class Order_Products(models.Model):
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.FloatField()
    class Meta: verbose_name_plural = 'Order_Products'