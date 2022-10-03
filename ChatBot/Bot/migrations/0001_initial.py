# Generated by Django 4.1.1 on 2022-10-03 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('phone_number', models.CharField(max_length=16, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_number', models.CharField(max_length=16)),
                ('to_number', models.CharField(max_length=16)),
                ('message_text', models.TextField()),
                ('sent_datetime', models.DateTimeField(auto_now=True)),
                ('contact_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bot.contact')),
            ],
        ),
    ]
