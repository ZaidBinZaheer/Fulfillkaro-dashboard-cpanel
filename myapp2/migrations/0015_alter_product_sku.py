# Generated by Django 4.1.2 on 2022-10-31 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp2', '0014_alter_bookinglog_pieces_alter_bookinglog_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(default=' ', max_length=50),
        ),
    ]