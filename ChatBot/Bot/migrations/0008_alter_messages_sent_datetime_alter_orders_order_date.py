# Generated by Django 4.1.1 on 2022-10-12 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0007_order_products_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='sent_datetime',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='orders',
            name='order_date',
            field=models.DateTimeField(),
        ),
    ]
