# Generated by Django 4.1.2 on 2022-10-24 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp2', '0007_product_alter_bookinglog_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.IntegerField(default=1),
        ),
    ]
