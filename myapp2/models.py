from email.policy import default
from unittest.util import _MAX_LENGTH
from django.db import models
# from django.contrib.auth.models import AbstractUser

# Create your models here.

class Nci(models.Model):
    record_no=models.AutoField(primary_key=True, default=0)
    username=models.CharField(max_length=100, default="")
    cn_number = models.BigIntegerField(default=0)
    name=models.CharField(max_length=100, default=" ")
    mobile_number=models.CharField(max_length=11,default=" ")
    address=models.CharField(max_length=100,default=" ")
    status=models.CharField(max_length=50,default=" ")
    choice=models.CharField(max_length=50,default=" ")

class Product(models.Model):

    product_no=models.AutoField(primary_key=True)
    username=models.CharField(max_length=100, default="")
    vendor_name=models.CharField(max_length=100, default=" ")
    product_name=models.CharField(max_length=50, default=" ")
    product_description=models.CharField(max_length=200, default=" ")
    # Stock Keeping Unit
    sku=models.CharField(max_length=50, default=" ")
    quantity_given=models.IntegerField(default=0)
    quantity_in_process=models.IntegerField(default=0)
    quantity_sold=models.IntegerField(default=0)
    quantity_available=models.IntegerField(default=0)
    product_image= models.FileField(upload_to='images/', null=True, verbose_name="")



class Customer(models.Model):
    username=models.CharField(max_length=50)
    customer_id=models.IntegerField(primary_key=True, default=523544)
    contact_no=models.CharField(max_length=12, default="920000000000")
    


class BookingLog(models.Model):

    record_no=models.AutoField(primary_key=True, default=0)
    cn_number = models.BigIntegerField(default=0)
    username=models.CharField(max_length=50, default=" ")
    name=models.CharField(max_length=100, default=" ")
    mobile_number=models.CharField(max_length=11,default=" ")
    email=models.CharField(max_length=50,default=" ")
    destination_city=models.CharField(max_length=50,default=" ")
    address=models.CharField(max_length=100,default=" ")
    default_origin_city=models.CharField(max_length=50,default=" ")
    weight=models.FloatField(default= 0.0)
    pieces=models.CharField(max_length=200,default=" ")
    customer_reference_number=models.CharField(max_length=50,default=" ")
    service_type=models.CharField(max_length=50,default=" ")
    flyer_number=models.CharField(max_length=50,default=" ")
    special_handling=models.CharField(max_length=50,default=" ")
    product_detail=models.CharField(max_length=100,default=" ")
    cash_amount=models.IntegerField(default=0)
    pickup_city=models.CharField(max_length=50,default=" ")
    status=models.CharField(max_length=50, default="Booked")
    dateTime=models.CharField(max_length=100, default="2022-10-21 11:57:13")
    manual=models.IntegerField(default=0)




class Booking(models.Model):
    
   
    cn_number = models.AutoField(primary_key=True, default="93610200000")
    username=models.CharField(max_length=50, default=" ")
    name=models.CharField(max_length=100, default=" ")
    mobile_number=models.CharField(max_length=11,default=" ")
    email=models.CharField(max_length=50,default=" ")
    destination_city=models.CharField(max_length=50,default=" ")
    address=models.CharField(max_length=100,default=" ")
    default_origin_city=models.CharField(max_length=50,default=" ")
    weight=models.FloatField(default= 0.0)
    pieces=models.IntegerField(default=0)
    customer_reference_number=models.CharField(max_length=50,default=" ")
    service_type=models.CharField(max_length=50,default=" ")
    flyer_number=models.CharField(max_length=50,default=" ")
    special_handling=models.CharField(max_length=50,default=" ")
    product_detail=models.CharField(max_length=100,default=" ")
    cash_amount=models.IntegerField(default=0)
    pickup_city=models.CharField(max_length=50,default=" ")
    status=models.CharField(max_length=50, default="Pending")





#  dateTime=models.CharField(max_length=100, default="21/10/2022 11:57:13")