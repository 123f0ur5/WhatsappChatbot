# Generated by Django 4.1.1 on 2022-10-07 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0002_rename_categorys_categories_alter_categories_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='deliver_address',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='description',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='orders',
            name='status',
            field=models.CharField(blank=True, max_length=12),
        ),
        migrations.AlterField(
            model_name='orders',
            name='total_value',
            field=models.FloatField(blank=True),
        ),
    ]