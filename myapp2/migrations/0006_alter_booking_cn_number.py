# Generated by Django 4.1.2 on 2022-10-22 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp2', '0005_alter_bookinglog_record_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='cn_number',
            field=models.AutoField(default='93610200000', primary_key=True, serialize=False),
        ),
    ]
