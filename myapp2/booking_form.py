from socket import fromshare
from django.forms import ModelForm
from django import forms
from .models import Booking

# def auto_increment(cn_number):
#     return cn_number+1
class BookingForm(ModelForm):

    cn_number=forms.TextInput()
    username=forms.TextInput()
    name=forms.TextInput()
    mobile_number=forms.TextInput()
    email=forms.TextInput()
    destination_city=forms.TextInput()
    address=forms.TextInput()
    default_origin_city=forms.TextInput()
    weight=forms.TextInput()
    pieces=forms.TextInput()
    customer_reference_number=forms.TextInput()
    service_type=forms.TextInput()
    flyer_number=forms.TextInput()
    special_handling=forms.TextInput()
    product_detail=forms.TextInput()
    cash_amount=forms.TextInput()
    pickup_city=forms.TextInput()
    status=forms.TextInput()
    class Meta:
        model = Booking
        fields=['cn_number', 'username', 'name', 'mobile_number', 'email', 'destination_city', 'address', 'default_origin_city', 'weight', 'pieces', 'customer_reference_number', 'service_type','flyer_number','special_handling','product_detail','cash_amount','pickup_city', 'status']