# Generated by Django 4.1.1 on 2022-10-07 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0004_rename_order_data_orders_order_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orders',
            old_name='description',
            new_name='Observation',
        ),
    ]
