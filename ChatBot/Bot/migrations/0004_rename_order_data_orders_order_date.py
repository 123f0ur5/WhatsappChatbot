# Generated by Django 4.1.1 on 2022-10-07 11:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0003_alter_orders_deliver_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orders',
            old_name='order_data',
            new_name='order_date',
        ),
    ]
