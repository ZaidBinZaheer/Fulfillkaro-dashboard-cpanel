from django import forms

from myapp2.models import Customer, Product


class ProductForm(forms.ModelForm):
   

    # username=forms.TextInput()
    # vendor_name=forms.TextInput()
    # product_name=forms.TextInput()
    # product_description=forms.TextInput()
    # # Stock Keeping Unit
    # sku=forms.TextInput()
    # quantity_given=forms.TextInput()
    # quantity_in_process=forms.TextInput()
    # quantity_sold=forms.TextInput()
    # quantity_available=forms.TextInput()
    # product_image=forms.ImageField()
    class Meta:
        model=Product
        fields= ["username", "vendor_name",'product_name', 'product_description','sku', 'quantity_given',
                'quantity_in_process','quantity_sold','quantity_available', 'product_image'  ]
