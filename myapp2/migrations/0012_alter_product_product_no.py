# Generated by Django 4.1.2 on 2022-10-24 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp2', '0011_alter_product_product_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_no',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
