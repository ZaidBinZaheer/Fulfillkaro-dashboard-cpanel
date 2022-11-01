from django.contrib import admin
from .models import Customer
from .models import BookingLog
from .models import Booking 
from .models import Product 

# Register your models here.

admin.site.register(Booking)
admin.site.register(BookingLog)
admin.site.register(Customer)
admin.site.register(Product)
