# Generated by Django 4.1.2 on 2022-10-22 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp2', '0002_customer_booking_status_booking_username_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingLog',
            fields=[
                ('record_no', models.AutoField(primary_key=True, serialize=False)),
                ('cn_number', models.IntegerField(default=0)),
                ('username', models.CharField(default=' ', max_length=50)),
                ('name', models.CharField(default=' ', max_length=100)),
                ('mobile_number', models.CharField(default=' ', max_length=11)),
                ('email', models.CharField(default=' ', max_length=50)),
                ('destination_city', models.CharField(default=' ', max_length=50)),
                ('address', models.CharField(default=' ', max_length=100)),
                ('default_origin_city', models.CharField(default=' ', max_length=50)),
                ('weight', models.FloatField(default=0.0)),
                ('pieces', models.IntegerField(default=0)),
                ('customer_reference_number', models.CharField(default=' ', max_length=50)),
                ('service_type', models.CharField(default=' ', max_length=50)),
                ('flyer_number', models.CharField(default=' ', max_length=50)),
                ('special_handling', models.CharField(default=' ', max_length=50)),
                ('product_detail', models.CharField(default=' ', max_length=100)),
                ('cash_amount', models.IntegerField(default=0)),
                ('pickup_city', models.CharField(default=' ', max_length=50)),
                ('status', models.CharField(default='Pending', max_length=50)),
            ],
        ),
    ]