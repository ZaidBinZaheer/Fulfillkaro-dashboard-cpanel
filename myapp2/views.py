# from asyncio.windows_events import NULL
from contextlib import nullcontext
# import email
from datetime import datetime, timedelta
from multiprocessing.sharedctypes import Value
from pprint import pprint
import statistics
from xmlrpc.client import DateTime
from django.shortcuts import render, redirect
import imp
from django.shortcuts import render
from django.http import HttpResponse
from myapp2.models import Booking, BookingLog, Customer, Nci
# from ..templates.raw_files.booking_form import BookingForm
from .models import Product
# from .ProductForm import ProductForm
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponseRedirect
import random
import requests
# import json
# import openpyxl
import pandas as pd
from django.http import JsonResponse

# Create your views here.

def index(request):

    if request.method=='POST':
        username=request.POST['username']
        if Booking.objects.filter(username=username).exists():
            last_booking_num=Booking.objects.filter(username=username).last().cn_number
            context={
            'last_cn_num' : last_booking_num+1    
            }
            return render(request, 'user_dashboard.html', context )
        else:
            if Customer.objects.filter(username=username).exists():
                cust_id=Customer.objects.filter(username=username).last().customer_id
                booking_no=0
                booking_no=str(booking_no).zfill(5)
                consignment_no=(str(cust_id)+booking_no)
                consignment_no=int(consignment_no)
                context={
                'last_cn_num' : consignment_no  
                 }
                return render(request, 'user_dashboard.html', context )
            else:
                cust_id= str(round(random.random()*1000000))
                while len(str(cust_id))!=6:
                    cust_id=(str(cust_id[:2]+"0"+cust_id[2:]))
                cust_id=int(cust_id)
                consignment_no=int(consignment_no)
                if Customer.objects.filter(customer_id=cust_id).exists():
                    messages.info(request, 'An error occured, Please try again !!! ')
                    return render(request, 'user_dashboard.html')
                customer=Customer.objects.create(username=username, customer_id=cust_id)
                customer.save()
                context={
                'last_cn_num' : consignment_no   
                }
                return render(request, 'user_dashboard.html', context )
      
    else:
        # messages.info(request, 'Not a POST method !!! ')
        return render(request, 'index.html', )




def register(request):
    if request.method == "POST":
        username=request.POST['username'];
        email=request.POST['email'];
        password=request.POST['password'];
        password2=request.POST['password2'];

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'This Email is already Registered !!! ')
                return redirect('index')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'This Username is already Registered !!! ')
                return redirect('index')
            else:
                cust_id= str(round(random.random()*1000000))
                while len(str(cust_id))!=6:
                    cust_id=(str(cust_id[:2]+"0"+cust_id[2:]))
                cust_id=int(cust_id)
                if Customer.objects.filter(customer_id=cust_id).exists():
                    messages.info(request, 'An error occured, Please try again !!! ')
                    return redirect('index')
                else:
                    customer=Customer.objects.create(username=username, customer_id=cust_id)
                    customer.save()
                    user=User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    messages.info(request, 'Signed up Successfully !!! ')
                    return redirect('index')
        else:
            messages.info(request, 'Password is NOT Same, Try Again  !!! ')
            return redirect('index')

    else:
        return render(request, 'index.html')



# def showBookingForm(request):
#     return 

def logout(request):
    auth.logout(request)
    return redirect('/')

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']

        user=auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            if username=='admin':
                total_bookings=len(BookingLog.objects.filter(status="Booked"))
                total_delivered_bookings=len(BookingLog.objects.filter( status='Delivered'))
                total_returned_bookings=len(BookingLog.objects.filter( status='Returned to Shipper'))
                stats={
                    'total_bookings':total_bookings,
                    'total_delivered_bookings':total_delivered_bookings,
                    'total_returned_bookings':total_returned_bookings,
                    'delivery_rate':round((total_delivered_bookings/(total_delivered_bookings+total_returned_bookings))*100, 2),
                    'return_rate':round((total_returned_bookings/(total_delivered_bookings+total_returned_bookings))*100, 2)
                }
                return render(request, 'admin_dashboard.html',stats)
    
            else:
                if (len(BookingLog.objects.filter(username=username, status='Delivered'))>0) | (len(BookingLog.objects.filter(username=username, status='Returned to Shipper'))>0) :
                    total_bookings=len(BookingLog.objects.filter(username=username, status="Booked"))
                    total_delivered_bookings=len(BookingLog.objects.filter(username=username, status='Delivered'))
                    total_returned_bookings=len(BookingLog.objects.filter(username=username, status='Returned to Shipper'))
                    stats={
                        'total_bookings':total_bookings,
                        'total_delivered_bookings':total_delivered_bookings,
                        'total_returned_bookings':total_returned_bookings,
                        'delivery_rate':round((total_delivered_bookings/(total_delivered_bookings+total_returned_bookings))*100,2),
                        'return_rate':round((total_returned_bookings/(total_delivered_bookings+total_returned_bookings))*100, 2)
                    }
                else:
                    total_bookings=len(BookingLog.objects.filter(username=username, status="Booked"))
                    total_delivered_bookings=len(BookingLog.objects.filter(username=username, status='Delivered'))
                    total_returned_bookings=len(BookingLog.objects.filter(username=username, status='Returned to Shipper'))
                   
                    stats={
                        'total_bookings':total_bookings,
                        'total_delivered_bookings':total_delivered_bookings,
                        'total_returned_bookings':total_returned_bookings,
                        'delivery_rate':0,
                        'return_rate':0.0
                }
                return render(request, 'user_dashboard.html',stats)
            

        else:
            messages.info(request, "Invalid Credentials !!!")
            return redirect('login')
    else:
        return render (request, 'index.html')


def after_booking(request):
    if request.method=='POST':
        # print("LENGTH IS :::::::::::::::::::::::::::::::::::::::::::",len(request.POST.keys())-15)
        allPs=[]
        allQs=[]
        
        m=int((len(request.POST.keys())-15)/2) # Change -15 to -16 if a new element is passed by Request.POST
        
        for i in range(1, m):
            t='p'
            u='q'
            t=t+str(i)
            u+=str(i)
            allPs.append(t)
            allQs.append(u)
        # print("======================== allPs: ", allPs)
        prod=request.POST[allPs[0]]
        quan=int(request.POST[allQs[0]])
        quan_in_str= request.POST[allQs[0]]
        username=request.POST['username']
        if len(allPs)>1:
            for i in range(len(allPs)):
                allPs[i]=request.POST[allPs[i]]
                allQs[i]=int(request.POST[allQs[i]])  

                updateQuant=Product.objects.get(username=username, product_description=allPs[i])
                updateQuant.quantity_available-=allQs[i]
                updateQuant.quantity_in_process+=allQs[i]
                updateQuant.save()

            for j in range(1, len(allPs)):
                prod+=", "+allPs[j]
                quan+=allQs[j]
                quan_in_str+=", "+str(allQs[j])
        else:
            updateQuant=Product.objects.get(username=username, product_description=prod)
            updateQuant.quantity_available-=quan
            updateQuant.quantity_in_process+=quan
            updateQuant.save()

        # print("*********** Product Details: "+prod)
        # print("----------- Quantity ",quan)

        cn_number=request.POST['cn_number']
        name=request.POST['name']
        mobile_number=request.POST['mobile_number']
        email=request.POST['email']
        destination_city=request.POST['destination_city']
        address=request.POST['address']
        default_origin_city=request.POST['default_origin_city']
        weight=request.POST['weight']
        pieces=quan_in_str
        customer_reference_number=request.POST['customer_reference_number']
        service_type=request.POST['service_type']
        flyer_number=request.POST['flyer_number']
        special_handling=request.POST['special_handling']
        product_detail=prod
        cash_amount=request.POST['cash_amount']
        pickup_city=request.POST['pickup_city']
        status=request.POST['status']
        manual=request.POST['manual']
        now = datetime.now()
        # dd-mm-YY H:M:S
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        dt_string = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        dt_string = dt_string + timedelta(hours=5)

        rec=BookingLog.objects.last().record_no
        rec+=1
        booking= BookingLog.objects.create(record_no=rec, cn_number=cn_number, username=username,  name=name, mobile_number=mobile_number, email=email, destination_city=destination_city, address=address, default_origin_city=default_origin_city, weight=weight, pieces=pieces,customer_reference_number=customer_reference_number,service_type=service_type, flyer_number=flyer_number, special_handling=special_handling , product_detail=product_detail,cash_amount=cash_amount,pickup_city=pickup_city, status=status, dateTime=dt_string, manual=manual)
        booking.save()

        messages.info(request, "Booking Done Successfully with CN # "+str(cn_number))
        return render(request, 'user_dashboard.html')
        # return render(request, 'after_booking.html', {'all_bookings': last_data})
    else:
        return render(request, 'user_dashboard.html')


def getBooking():
    pass


def lastbooking(request):

    # all_bookings=Booking.objects.all()
    if request.method=='POST':
        booking_of=request.POST['username']
        if Booking.objects.filter(username=booking_of).exists():
            specific_booking=Booking.objects.get(username=booking_of)
            return render(request, 'user_dashboard.html', {'all_bookings': specific_booking} )
        else:
            messages.info(request, "You have NOT made any Booking yet !!!")
            return redirect('/')
    else:
        messages.info(request, "Try Again !!!")
        return redirect('/')
        # last_data=Booking.objects.last()
    


def goto_home(request):
    return render(request, 'index.html')

def get_last(request):
    if request.method=='POST':
        username=request.POST['username']
        if Product.objects.filter(username=username).exists():
            
            products_with_this_user=Product.objects.filter(username=username)
            # print(products_with_this_user.last().product_description)

            # product_list=[]
            # for i in range (len(products_with_this_user)):
            #     product_list.append(products_with_this_user[i].product_name)
        else:
            messages.info(request, 'We do NOT have your Stock Yet !!!')
            return render(request, 'user_dashboard.html')

        if BookingLog.objects.filter(username=username).exists():
            # print("**************"+products_with_this_user.last().product_description)
            last_booking_num=BookingLog.objects.filter(username=username, status='Booked').last().cn_number
            context={
            'last_cn_num' : last_booking_num+1,
            'products_with_this_user':products_with_this_user
            }
            return render(request, 'user_dashboard.html', context )
        else:
            if Customer.objects.filter(username=username).exists():
                cust_id=Customer.objects.filter(username=username).last().customer_id
                booking_no=0
                booking_no=str(booking_no).zfill(5)
                consignment_no=(str(cust_id)+booking_no)
                consignment_no=int(consignment_no)
                context={
                'last_cn_num' : consignment_no ,
                'products_with_this_user':products_with_this_user 
                 }
                return render(request, 'user_dashboard.html', context )
            else:
                cust_id= str(round(random.random()*1000000))
                while len(str(cust_id))!=6:
                    cust_id=(str(cust_id[:2]+"0"+cust_id[2:]))
                cust_id=int(cust_id)
                booking_no=0
                booking_no=str(booking_no).zfill(5)
                consignment_no=(str(cust_id)+booking_no)
                consignment_no=int(consignment_no)
                if Customer.objects.filter(customer_id=cust_id).exists():
                    messages.info(request, 'An error occured, Please try again !!! ')
                    return render(request, 'user_dashboard.html')
                customer=Customer.objects.create(username=username, customer_id=cust_id)
                customer.save()
                context={
                'last_cn_num' : consignment_no,
                'products_with_this_user':products_with_this_user
                }
                return render(request, 'user_dashboard.html', context )
      
    else:
        messages.info(request, 'Not a POST method !!! ')
        return render(request, 'index.html', )


def editProduct(request):
    # product_name=request.POST['product_name']
    # product_description=request.POST['product_description']
    sku=request.POST['sku']
    quantity_given=request.POST['quantity_given']
    quantity_in_process=request.POST['quantity_in_process']
    quantity_sold=request.POST['quantity_sold']
    quantity_available=request.POST['quantity_available']

    p=Product.objects.get(sku=sku)
    # p.product_name=product_name
    # p.product_description=product_description
    p.quantity_given=quantity_given
    p.quantity_in_process=quantity_in_process
    p.quantity_sold=quantity_sold
    p.quantity_available=quantity_available
    p.save()
    return render(request, 'admin_dashboard.html')


    pass




def show_bookings(request):
    all_bookings=Booking.objects.all()
    return render(request, 'admin_dashboard.html', {'all_bookings':all_bookings})

def done_booking(request):
    
    all_bookings=BookingLog.objects.all()
    # return redirect('/', {'all_bookings':all_bookings} )
    return render(request, 'admin_dashboard.html', {'all_bookings':all_bookings})


def save_changes(request):
    updated_status=request.POST['status']
    cn_num=request.POST['cn_number']
    record=BookingLog.objects.filter(cn_number=cn_num).last()
    username=record.username
    print("USERNAME IS ----------> "+username)
    name=record.name
    mobile_number=record.mobile_number
    email=record.email
    destination_city=record.destination_city
    address=record.address
    default_origin_city=record.default_origin_city
    weight=record.weight
    piecess=record.pieces
    customer_reference_number=record.customer_reference_number
    service_type=record.service_type
    flyer_number=record.flyer_number
    special_handling=record.special_handling
    product_detail=record.product_detail
    cash_amount=record.cash_amount
    pickup_city=record.pickup_city
    manual=record.manual
    status=updated_status
    
    
    now = datetime.now()
        # dd-mm-YY H:M:S
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    dt_string = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
    dt_string = dt_string + timedelta(hours=5)
    
    rec=BookingLog.objects.last().record_no
    rec+=1

    new_rec= BookingLog.objects.create(record_no=rec, cn_number=cn_num, username=username,  name=name, mobile_number=mobile_number, email=email, destination_city=destination_city, address=address, default_origin_city=default_origin_city, weight=weight, pieces=piecess,customer_reference_number=customer_reference_number,service_type=service_type, flyer_number=flyer_number, special_handling=special_handling , product_detail=product_detail,cash_amount=cash_amount,pickup_city=pickup_city, status=status, dateTime=dt_string, manual=manual )
    new_rec.save()

    # n_product=request.POST['product_description']
    # n_pieces=request.POST['pieces']
    if updated_status=="Refused by Customer":
        recN=0
        if Nci.objects.all().exists():
            recN=Nci.objects.last().record_no+1
        new_nci=Nci.objects.create(record_no=recN, username=username, cn_number=cn_num, name=name, mobile_number=mobile_number, address=address, status="active", choice="-")
        new_nci.save()

        # SENDING SMS TO CUSTOMER USING LIFETIME SMS API
        cust_id=cn_num[:6]
        # print("Customer ID  is : "+cust_id)
        customer_contact=Customer.objects.get(customer_id=cust_id).contact_no
        # print("Customer Contact Number is : "+customer_contact)
        api_token = "9b22f7e90c6b3f3042ea5664a3acc4ca72c47a3294" # Your api_token key.
        api_secret = "FulfillkaroSMSAPISecretKey" # Your api_token key.
        # to = "923xxxxxxxxx,923xxxxxxxxx,923xxxxxxxxx" # Multiple mobiles numbers separated by comma.
        to=customer_contact
        from_ = "fulfil" # Sender ID,Max 6 characters long.
        message = 'Hello '+username+'! \nNotification: One of your orders with Consignment Number '+cn_num+' has been Refused by your Customer. Kindly log in to Portal and make your choice to either "Return the Parcel" or "Go for Re-attempt".\nRegards Fulfillkaro.pk' # Your message to send.
        # Prepare you post parameters
        values = {
                "api_token" : api_token,
                "api_secret" : api_secret,
                "to" : to,
                "from" : from_,
                "message" : message
                }
        url = "https://lifetimesms.com/json" # API URL
        r = requests.post(url = url,json=values, data = values)    
        # extracting response text 
        pastebin_url = r.text
        # print("The pastebin URL is:%s"%pastebin_url)



    elif (updated_status=="Delivered") | (updated_status=="Returned to Shipper"):

        if ',' in str(piecess):
            piec=piecess.split(", ")
            prod=product_detail.split(", ")
        else:
            piec=[piecess]
            prod=[product_detail]
            print("**************************************")
            print(piec)
            print(prod)

        if Product.objects.filter(username=username).exists():
            if updated_status == "Delivered":
                for i in range(len(prod)):
                    pro=Product.objects.get(product_description=prod[i])
                    pro.quantity_in_process-=int(piec[i])
                    pro.quantity_sold+=int(piec[i])
                    pro.save()
            elif updated_status == "Returned to Shipper":
                for i in range(len(prod)):
                    pro=Product.objects.get(product_description=prod[i])
                    pro.quantity_in_process-=int(piec[i])
                    pro.quantity_available+=int(piec[i])
                    pro.save()
        
        else:
            messages.info(request, "No such Product with this Username !!! ")
            return render(request, 'admin_dashboard.html', )
        # reattempt=request.POST['reattempt']
        # if reattempt=="1":
        #     delete_reattempt=BookingLog.objects.filter(cn_number=cn_num, status="Re-attempt the Booking")| BookingLog.objects.filter(cn_number=cn_num, status="Ready for Return")
        #     delete_reattempt.delete()   
    return render(request, 'admin_dashboard.html')
    





def delete_booking(request):
    print("--------------------------"+request.POST['cn_number'])
    cn_number=request.POST['cn_number']
    statu=request.POST['statu'] 
    
    member = BookingLog.objects.filter(cn_number=cn_number, status=statu).last()
    member.delete()
    return render(request, 'admin_dashboard.html')


def menu(request):
    pass
    

def getStatistics(request):
    username=request.POST['username']
    if username=='admin':
        total_bookings=len(BookingLog.objects.filter(status="Booked"))
        total_delivered_bookings=len(BookingLog.objects.filter( status='Delivered'))
        total_returned_bookings=len(BookingLog.objects.filter( status='Returned to Shipper'))
        stats={
            'total_bookings':total_bookings,
            'total_delivered_bookings':total_delivered_bookings,
            'total_returned_bookings':total_returned_bookings,
            'delivery_rate':round((total_delivered_bookings/(total_delivered_bookings+total_returned_bookings))*100, 2),
            'return_rate':round((total_returned_bookings/(total_delivered_bookings+total_returned_bookings))*100, 2)
        }
        return render(request, 'admin_dashboard.html',stats)
    else:
        if (len(BookingLog.objects.filter(username=username, status='Delivered'))>0) | (len(BookingLog.objects.filter(username=username, status='Returned to Shipper'))>0) :
            total_bookings=len(BookingLog.objects.filter(username=username, status="Booked"))
            total_delivered_bookings=len(BookingLog.objects.filter(username=username, status='Delivered'))
            total_returned_bookings=len(BookingLog.objects.filter(username=username, status='Returned to Shipper'))
            stats={
                    'total_bookings':total_bookings,
                    'total_delivered_bookings':total_delivered_bookings,
                    'total_returned_bookings':total_returned_bookings,
                    'delivery_rate':round((total_delivered_bookings/(total_delivered_bookings+total_returned_bookings))*100,2),
                    'return_rate':round((total_returned_bookings/(total_delivered_bookings+total_returned_bookings))*100, 2)
                }
        else:
            total_bookings=len(BookingLog.objects.filter(username=username, status="Booked"))
            total_delivered_bookings=len(BookingLog.objects.filter(username=username, status='Delivered'))
            total_returned_bookings=len(BookingLog.objects.filter(username=username, status='Returned to Shipper'))

            stats={
                'total_bookings':total_bookings,
                'total_delivered_bookings':total_delivered_bookings,
                'total_returned_bookings':total_returned_bookings,
                'delivery_rate':0,
                'return_rate':0.0
                }
        return render(request, 'user_dashboard.html',stats)



def getLog(request):
    cn_number=request.POST['cn_number']
    username=request.POST['username']
    
    # return redirect('/', {'all_bookings':all_bookings} )
    if username=='admin':
        if len(cn_number)==9:
            url='http://new.leopardscod.com/webservice/trackBookedPacket/?'

            querystring={
            'api_key' : 'D8C01F4A1E2115914D0A7D20369B2644',
            'api_password' : 'HUSNAIN1@1',
            'track_numbers' : cn_number   
            }
            response=requests.get(url, params=querystring).json()
            if response['packet_list'][0]['Tracking Detail']!= None:
                # print(json.dumps(response.json(), indent=4, sort_keys=True))
                leapord_order_id=response['packet_list'][0]['booked_packet_order_id']
                # print(leapord_order_id)
                b=BookingLog.objects.filter(customer_reference_number=leapord_order_id)
                # print(b.last().cn_number)
                return render(request, 'admin_dashboard.html', {'bookings_log':b})
            else:
                messages.info(request, "No Record Found !!! ")
            return render(request, 'admin_dashboard.html')
        else:
            bookings_log=BookingLog.objects.filter(cn_number=cn_number)
            return render(request, 'admin_dashboard.html', {'bookings_log':bookings_log})
    else:
        bookings_log=BookingLog.objects.filter(cn_number=cn_number)
        return render(request, 'user_dashboard.html', {'bookings_log':bookings_log})


# Search CN Number Wise
def searchRecord(request):
    cn_num=request.POST['cn_number']
    # username=request.POST['username']
    if BookingLog.objects.filter(cn_number=cn_num).exists():
        your_record=BookingLog.objects.filter(cn_number=cn_num).last()
        return render(request, 'user_dashboard.html', {'rec': your_record})
    else:
        messages.info(request, "No Record with this Consignment Number !!!")
        return render(request, 'user_dashboard.html')


def searchDateWise(request):    
    # messages.info(request, "In a Maintainance Process! You Might see inaccurate/unexpected Data")
    
    from_date=request.POST['from_date']
    # to_date=request.POST['to_date']
    c=request.POST['to_date']
    to_date=add_1_day_to_date(c)
    # print(to_date)


    username=request.POST['username']
    rec=BookingLog()
    this_rec=[]
    status=request.POST['status']
    
    if username=="admin":
        
        if status=='All Bookings':
            rec=BookingLog.objects.filter(dateTime__range=[from_date, to_date])
            # print(rec)
        else:
            rec=BookingLog.objects.filter(dateTime__range=[from_date, to_date])
            cn=[]
            for i in range(len(rec)):
                if rec[i].cn_number not in cn:
                    cn.append(rec[i].cn_number)
            if status=='Manual':
                for i in range(len(cn)):
                    if rec.filter(cn_number=cn[i]).last().manual==1:
                        this_rec.append(rec.filter(cn_number=cn[i], manual=1).last())
                if this_rec==[]:
                    messages.info(request, "No Record Found !!!")
                return render(request, 'admin_dashboard.html',{'bookings_log': this_rec} )
            else:
                for i in range(len(cn)):
                    if rec.filter(cn_number=cn[i]).last().status==status:
                        this_rec.append(rec.filter(cn_number=cn[i], status=status).last())
                if this_rec==[]:
                    messages.info(request, "No Record Found !!!")
                return render(request, 'admin_dashboard.html',{'bookings_log': this_rec} )
    else:
        if status=='All Bookings':
            rec=BookingLog.objects.filter(username=username, dateTime__range=[from_date, to_date])
            # print(rec)
        else:
            rec=BookingLog.objects.filter(username=username, dateTime__range=[from_date, to_date])
            cn=[]
            for i in range(len(rec)):
                if rec[i].cn_number not in cn:
                    cn.append(rec[i].cn_number)
            for i in range(len(cn)):
                if rec.filter(cn_number=cn[i]).last().status==status:
                    this_rec.append(rec.filter(cn_number=cn[i], status=status).last())
            if this_rec==[]:
                messages.info(request, "No Record Found !!!")
            return render(request, 'user_dashboard.html',{'all_bookings': this_rec} )
    cn_list=[]
    for i in range(len(rec)):
        if rec[i].cn_number not in cn_list:
            cn_list.append(rec[i].cn_number)
    # print("**************************", cn_list)
    filtered_rec=[]
    for i in range(len(cn_list)):
        filtered_rec.append(rec.filter(cn_number=cn_list[i]).last())
    # print("---------------------"+ filtered_rec[0].status +"-------------"+ filtered_rec[1].status)

    # print(username, "***************************"+from_date+"*********************"+to_date+"*********** Total records in this time range: ", len(rec))
    # *"+rec[0].dateTime+"******"+rec[1].dateTime)
    if filtered_rec == []:
        if username=="admin":
            messages.info(request, "No Record in this Time Range !!!")
            return render(request, 'admin_dashboard.html')
            # return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        else:
            messages.info(request, "No Record in this Time Range !!!")
            # return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            return render(request, 'user_dashboard.html')
    else:
        if username=="admin":
            return render(request, 'admin_dashboard.html',{'bookings_log': filtered_rec} )
        else:
            return render(request, 'user_dashboard.html',{'all_bookings': filtered_rec} )



def cancelRecord(request):
    cn_number=request.POST['cn_number']
    rec=Booking.objects.get(cn_number=cn_number)
    rec.status="Refused by Customer"
    rec.save()
    messages.info(request, "Booking Canceled successfully !!!")
    return render(request, 'user_dashboard.html')



def showProduct():
    pass


def goto_Product_Page():
    pass
    # return render(request, 'Product.html')


def save_stock_record(request):
    sku=request.POST['sku']
    if Product.objects.filter(sku=sku).exists():
        messages.info(request, "SKU Already Exists, Try Another !!!")
        return render(request, 'admin_dashboard.html')
    else:
        username=request.POST['username']
        vendor_name=request.POST['vendor_name']
        product_name=request.POST['product_name']
        product_description=request.POST['product_description']
        quantity_given=request.POST['quantity_given']
        quantity_in_process=0
        quantity_sold=0
        quantity_available=request.POST['quantity_given']
        product_image=request.FILES['product_image']
        new_stock=Product.objects.create(username=username, vendor_name=vendor_name, product_name=product_name,
        product_description=product_description, sku=sku, quantity_given=quantity_given,
        quantity_in_process=quantity_in_process, quantity_sold=quantity_sold,
            quantity_available=quantity_available, product_image=product_image )
        new_stock.save()
    
        return render(request, 'admin_dashboard.html')



def showProducts(request):
    username=request.POST['username']
    if Product.objects.filter(username=username).exists():
        products_with_this_user=Product.objects.filter(username=username)
        if request.POST['amiadmin']=="0":
            return render(request, 'user_dashboard.html', {'all_Products':products_with_this_user})
        else:
            return render(request, 'admin_dashboard.html', {'all_Products':products_with_this_user})
    else:
        if request.POST['amiadmin']=="0":
            messages.info(request, 'We do NOT have your Stock Yet !!!')
            return render(request, 'user_dashboard.html')
        else:
            messages.info(request, 'No Stock !!!')
            return render(request, 'admin_dashboard.html')

    
def showAllCustomers(request):

    context={
        'username':[],
        'customer_id':[]
    }
    all_u=User.objects.all()
    
    print(all_u)

    for i in range (len(all_u)):
        # print("********************* User ", (i+1), " ************")
        context['username'].append(all_u[i].username)
                
        # print("Username: "+all_u[i].username)
        if Customer.objects.filter(username=all_u[i].username).exists():
            customer_id=Customer.objects.get(username=all_u[i].username).customer_id
            context['customer_id'].append(customer_id)
            # print("Customer Id: ",customer_id)
    return render(request, 'admin_dashboard.html', {'context':context} )

    

def show_api(request):
    leapord_tracking_number=request.POST['leapord_tracking_number']
    username=request.POST['username']
    if len(leapord_tracking_number)==9:
        # messages.info(request, 'You Entered: '+leapord_tracking_number)

        url='http://new.leopardscod.com/webservice/trackBookedPacket/?'

        querystring={
        'api_key' : 'D8C01F4A1E2115914D0A7D20369B2644',
        'api_password' : 'HUSNAIN1@1',
        'track_numbers' : leapord_tracking_number   
        }
        response=requests.get(url, params=querystring).json()
        if response['packet_list'][0]['Tracking Detail']!= None:
            # print(json.dumps(response.json(), indent=4, sort_keys=True))
            tracking_detail=response['packet_list'][0]['Tracking Detail']
            other_detail={

                'booking_date': response['packet_list'][0]['booking_date'],
                'track_number': response['packet_list'][0]['track_number'],
                'arival_dispatch_weight': round((int(response['packet_list'][0]['arival_dispatch_weight'])/1000), 4),
                'booked_packet_no_piece': response['packet_list'][0]['booked_packet_no_piece'],
                'booked_packet_collect_amount': response['packet_list'][0]['booked_packet_collect_amount'],
                'booked_packet_order_id': response['packet_list'][0]['booked_packet_order_id'],
                'origin_city_name': response['packet_list'][0]['origin_city_name'],
                'destination_city_name': response['packet_list'][0]['destination_city_name'],
                'shipment_name_eng': response['packet_list'][0]['shipment_name_eng'],
                'shipment_address': response['packet_list'][0]['shipment_address'],
                'consignment_name_eng': response['packet_list'][0]['consignment_name_eng'],
                'consignment_address': response['packet_list'][0]['consignment_address'],
                'consignment_phone': response['packet_list'][0]['consignment_phone'],
                
                'td': tracking_detail
            }
            more_detail=[]
            more_detail.append(other_detail)

        else:
            messages.info(request, 'No Record with Tracking # '+leapord_tracking_number)
            if username=='admin':
                return render(request, 'admin_dashboard.html')
            else:
                return render(request, 'user_dashboard.html')
        if username=='admin':
            return render(request, 'admin_dashboard.html', {'tracking_detail':more_detail})
        else:
            return render(request, 'user_dashboard.html', {'tracking_detail':more_detail})
    else:
        if BookingLog.objects.filter(cn_number=leapord_tracking_number).exists():
            booking_id=BookingLog.objects.filter(cn_number=leapord_tracking_number).last().customer_reference_number
            url = "http://new.leopardscod.com/webservice/getShipmentDetailsByOrderID/format/json/"

            headerz = {
                "content-type": "application/json"
            }

            # API KEY and Password
            API_KEY = "D8C01F4A1E2115914D0A7D20369B2644"
            API_PASSWORD="HUSNAIN1@1"
            # Order Id(s)
            SHIPMENT_ID= []
            SHIPMENT_ID.append(booking_id)

            # SHIPMENT_ID=json.dumps(SHIPMENT_ID)

            querystring = {
                'api_key' : API_KEY,
                'api_password' : API_PASSWORD,
                'shipment_order_id' : SHIPMENT_ID
            }

            # sending post request and saving response as response object
            r = requests.post(url = url, json=querystring, headers=headerz )

            output = r.json()
            # print("The Output is:%s"%output)
            actual_leapord_tracking_number=output['data'][0]['track_number_short']
            
            url='http://new.leopardscod.com/webservice/trackBookedPacket/?'

            querystring={
            'api_key' : 'D8C01F4A1E2115914D0A7D20369B2644',
            'api_password' : 'HUSNAIN1@1',
            'track_numbers' : actual_leapord_tracking_number   
            }
            response=requests.get(url, params=querystring).json()
            if response['packet_list'][0]['Tracking Detail']!= None:
                # print(json.dumps(response.json(), indent=4, sort_keys=True))
                tracking_detail=response['packet_list'][0]['Tracking Detail']
                other_detail={

                    'booking_date': response['packet_list'][0]['booking_date'],
                    'track_number': response['packet_list'][0]['track_number'],
                    'arival_dispatch_weight': round((int(response['packet_list'][0]['arival_dispatch_weight'])/1000), 3),
                    'booked_packet_no_piece': response['packet_list'][0]['booked_packet_no_piece'],
                    'booked_packet_collect_amount': response['packet_list'][0]['booked_packet_collect_amount'],
                    'booked_packet_order_id': response['packet_list'][0]['booked_packet_order_id'],
                    'origin_city_name': response['packet_list'][0]['origin_city_name'],
                    'destination_city_name': response['packet_list'][0]['destination_city_name'],
                    'shipment_name_eng': response['packet_list'][0]['shipment_name_eng'],
                    'shipment_address': response['packet_list'][0]['shipment_address'],
                    'consignment_name_eng': response['packet_list'][0]['consignment_name_eng'],
                    'consignment_address': response['packet_list'][0]['consignment_address'],
                    'booked_packet_id': response['packet_list'][0]['booked_packet_id'],

                    'td': tracking_detail
                }
                more_detail=[]
                more_detail.append(other_detail)

            else:
                messages.info(request, 'No Record with Tracking # '+leapord_tracking_number)
                if username=='admin':
                    return render(request, 'admin_dashboard.html')
                else:
                    return render(request, 'user_dashboard.html')


            if username=='admin':
                return render(request, 'admin_dashboard.html', {'tracking_detail':more_detail})
            else:
                return render(request, 'user_dashboard.html', {'tracking_detail':more_detail})

        else:
            messages.info(request, 'No Record with Tracking # '+leapord_tracking_number)
            if username=='admin':
                return render(request, 'admin_dashboard.html')
            else:
                return render(request, 'user_dashboard.html')


    # return render(request, 'admin_dashboard.html', {'tracking_detail':more_detail})

            
        # else:
        #     messages.info(request, 'No Record with Tracking # '+leapord_tracking_number)
        # return render(request, 'admin_dashboard.html')


def get_tracking_record_of_specific_user_record(request):
    username=request.POST['username']
    b=BookingLog.objects.filter(username=username)
    cn_l=[]
    
    for i in range(len(b)):
        if b[i].cn_number not in cn_l:
            cn_l.append(b[i].cn_number)
    # PREVIOUS BOOKINGS (date till 19 November 2022)
    from_d="2022-10-10 08:00:00"
    to_d="2022-11-20 08:00:00"

    not_previous_cn=[]
    filtered_rec=[]
    for i in range(len(cn_l)):
        if BookingLog.objects.filter(cn_number=cn_l[i], status="Booked", dateTime__range=[from_d, to_d]).exists():
            filtered_rec.append(BookingLog.objects.filter(cn_number=cn_l[i]).last())
            # if cn_l[i]==16581200034:
            #     messages.info(request, BookingLog.objects.filter(cn_number=cn_l[i], dateTime__range=[from_d, to_d]).last().status)
        else:
            not_previous_cn.append(cn_l[i])
    if not_previous_cn==[]:
        # all bookings are previous
        # print(filtered_rec[len(filtered_rec)-1].status)
        return render(request, 'user_dashboard.html',{'all_bookings': filtered_rec} )
    else:
        last_90=[]
        for i in range(len(not_previous_cn)):
            if not_previous_cn[i] not in last_90:
                last_90.append(not_previous_cn[i])
        last_90.sort()
        not_previous_cn=last_90[-90:]
        # print(not_previous_cn)
        # messages.info(request,  not_previous_cn)
        booking_id=[]
        for i in range(len(not_previous_cn)):
            booking_id.append(BookingLog.objects.filter(cn_number=not_previous_cn[i]).last().customer_reference_number)
        # messages.info(request,  booking_id)
        # booking_id.sort()
        url = "http://new.leopardscod.com/webservice/getShipmentDetailsByOrderID/format/json/"
        headerz = {
            "content-type": "application/json"
        }
        # API KEY and Password
        API_KEY = "D8C01F4A1E2115914D0A7D20369B2644"
        API_PASSWORD="HUSNAIN1@1"
        # Order Id(s)
        SHIPMENT_ID= booking_id
        # SHIPMENT_ID=json.dumps(SHIPMENT_ID)
        querystring = {
            'api_key' : API_KEY,
            'api_password' : API_PASSWORD,
            'shipment_order_id' : SHIPMENT_ID
        }
        # sending post request and saving response as response object
        r = requests.post(url = url, json=querystring, headers=headerz )
        output = r.json()
        s=[]
        # v=""
        if output['error']=="":
            for i in range(len(output['data'])):
                s.append(output['data'][i])
                # v+=s[i]['consignment_name_eng']+", "+s[i]['booked_packet_order_id']+", "
            
        else:
            messages.info(request,  "An Error (API Error) Occured. Please Contact Management! ")
            # Status may be inaccurate
            return render(request, 'user_dashboard.html',{'all_bookings': filtered_rec} )
        # messages.info(request, s[i]['consignment_phone'])
        api_received_phone=[]
        for i in range(len(s)):
            api_received_phone.append(s[i]['consignment_phone'])
        if len(s)==len(not_previous_cn):
            # messages.info(request,  str(BookingLog.objects.filter(cn_number=not_previous_cn[0]).last().mobile_number)+" "+str(s[0]['consignment_phone']))
            for i in range(len(not_previous_cn)):
                filtered_rec.append(BookingLog.objects.filter(mobile_number=api_received_phone[i]).last())
                # if BookingLog.objects.filter(cn_number=not_previous_cn[i]).last().mobile_number==s[i]['consignment_phone']:
                #     # messages.info(request,  filtered_rec[0])
                filtered_rec[len(filtered_rec)-1].status=s[i]['booked_packet_status']
                    
            # messages.info(request,  str(not_previous_cn[len(not_previous_cn)-1])+" ."+ str(filtered_rec[len(filtered_rec)-1].mobile_number)+". "+ filtered_rec[len(filtered_rec)-1].status)

            return render(request, 'user_dashboard.html',{'all_bookings': filtered_rec} )
        else:

            messages.info(request,  "An Error (Length "+str(len(s))+" and "+str(len(not_previous_cn))+" Mismatch Error) Occured. You might be unable to view some booking  ")
            return render(request, 'user_dashboard.html',{'all_bookings': filtered_rec} )

        # return render(request, 'user_dashboard.html')
        

  
def get_nci(request):
    username=request.POST['username']
    
    if Nci.objects.filter(username=username, status="active").exists():
        print("USERNAME IS : "+username)
        active_nci=Nci.objects.filter(username=username, status="active", choice="-")
        return render(request, 'user_dashboard.html',{'active_nci': active_nci} )

    else:
        msg="No Record Found !"
        return render(request, 'user_dashboard.html', {'msg': msg} )
    
def updated_nci_booking(request):
    length_of_request_received= len(request.POST)
    choice=""
    if length_of_request_received > 4:
        choice=request.POST['choice']

    else:
        choice="1"

    if choice=="1":
        print('********************************** USER CHOSE FOR RE-ATTEMPT ********************')
        new_contact=request.POST['new_contact']
        new_address=request.POST['new_address']
        cn_number=request.POST['cn_number']
        update_Booking_log=BookingLog.objects.filter(cn_number=cn_number).last()
        
        new_status="Re-attempt the Booking"
        # update_Booking_log.save()
        rec=BookingLog.objects.last().record_no
        rec+=1
        now = datetime.now()
        # dd-mm-YY H:M:S
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        dt_string = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        dt_string = dt_string + timedelta(hours=5)
        booking= BookingLog.objects.create(record_no=rec, cn_number=cn_number, username=update_Booking_log.username,  name=update_Booking_log.name, mobile_number=new_contact, email=update_Booking_log.email, destination_city=update_Booking_log.destination_city, address=new_address, default_origin_city=update_Booking_log.default_origin_city, weight=update_Booking_log.weight, pieces=update_Booking_log.pieces,customer_reference_number=update_Booking_log.customer_reference_number,service_type=update_Booking_log.service_type, flyer_number=update_Booking_log.flyer_number, special_handling=update_Booking_log.special_handling , product_detail=update_Booking_log.product_detail,cash_amount=update_Booking_log.cash_amount,pickup_city=update_Booking_log.pickup_city, status=new_status, dateTime=dt_string, manual= update_Booking_log.manual )
        booking.save()
        # delete_nci_record=Nci.objects.filter(cn_number=cn_number)
        # delete_nci_record.delete()
        change_status=Nci.objects.filter(cn_number=cn_number).last()
        if change_status.status=='active':
            recN=0
            if Nci.objects.exists():
                recN=Nci.objects.last().record_no+1
            new_nci=Nci.objects.create(record_no=recN, username=change_status.username, cn_number=change_status.cn_number, name=change_status.name, mobile_number=new_contact, address=new_address, status="active", choice='Re-attempt')
            new_nci.save()
        change_status.status="inactive"
        change_status.save()
        message = 'Notification: '+change_status.username+' has asked for  "Re-attempt" against CN # '+ str(change_status.cn_number)

    else:
        print('********************************** USER CHOSE FOR RETURN ********************')
        cn_number=request.POST['cn_number']
        update_Booking_log=BookingLog.objects.filter(cn_number=cn_number).last()
        
        new_status="Ready for Return"
        # update_Booking_log.save()
        rec=BookingLog.objects.last().record_no
        rec+=1
        now = datetime.now()
        # dd-mm-YY H:M:S
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        dt_string = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        dt_string = dt_string + timedelta(hours=5)
        booking= BookingLog.objects.create(record_no=rec, cn_number=cn_number, username=update_Booking_log.username,  name=update_Booking_log.name, mobile_number=update_Booking_log.mobile_number, email=update_Booking_log.email, destination_city=update_Booking_log.destination_city, address=update_Booking_log.address, default_origin_city=update_Booking_log.default_origin_city, weight=update_Booking_log.weight, pieces=update_Booking_log.pieces,customer_reference_number=update_Booking_log.customer_reference_number,service_type=update_Booking_log.service_type, flyer_number=update_Booking_log.flyer_number, special_handling=update_Booking_log.special_handling , product_detail=update_Booking_log.product_detail,cash_amount=update_Booking_log.cash_amount,pickup_city=update_Booking_log.pickup_city, status=new_status, dateTime=dt_string, manual=update_Booking_log.manual )
        booking.save()
        # delete_nci_record=Nci.objects.filter(cn_number=cn_number)
        # delete_nci_record.delete()
        change_status=Nci.objects.filter(cn_number=cn_number).last()
        if change_status.status=='active':
            recN=0
            if Nci.objects.exists():
                recN=Nci.objects.last().record_no+1
            new_nci=Nci.objects.create(record_no=recN, username=change_status.username, cn_number=change_status.cn_number, name=change_status.name, mobile_number=change_status.mobile_number, address=change_status.address, status="active", choice='Return')
            new_nci.save()
        change_status.status="inactive"
        change_status.save()

        message = 'Notification: '+change_status.username+' has asked to "Return the Parcel" against CN # '+ str(change_status.cn_number)

        # cn_number=request.POST['cn_number']
        # update_Booking_log=BookingLog.objects.filter(cn_number=cn_number).last()
        # update_Booking_log.status="Ready for Return"
        # update_Booking_log.save()
        # # delete_nci_record=Nci.objects.filter(cn_number=cn_number)
        # # delete_nci_record.delete()
        # change_status=Nci.objects.get(cn_number=cn_number, status="active")
        # change_status.status="inactive"
        # change_status.save()
       
    api_token = "9b22f7e90c6b3f3042ea5664a3acc4ca72c47a3294" # Your api_token key.
    api_secret = "FulfillkaroSMSAPISecretKey" # Your api_token key.
    # to = "923xxxxxxxxx,923xxxxxxxxx,923xxxxxxxxx" # Multiple mobiles numbers separated by comma.
    to="923405125632"
    # to="923135003799"
    from_ = "fulfil" # Sender ID,Max 6 characters long.
    # Prepare you post parameters
    values = {
            "api_token" : api_token,
            "api_secret" : api_secret,
            "to" : to,
            "from" : from_,
            "message" : message
            }
    url = "https://lifetimesms.com/json" # API URL
    r = requests.post(url = url,json=values, data = values)    
    # extracting response text 
    pastebin_url = r.text
    # print("The pastebin URL is:%s"%pastebin_url)

    # print("USER SELECTED:      "+choice)
    return render(request, 'user_dashboard.html')


def get_nci_for_admin(request):
    # if (BookingLog.objects.filter(status="Re-attempt the Booking").exists()) | (BookingLog.objects.filter(status="Ready for Return").exists()):
    #     active_nci=BookingLog.objects.filter(status="Re-attempt the Booking")| BookingLog.objects.filter(status="Ready for Return")
    #     return render(request, 'admin_dashboard.html',{'active_nci': active_nci} )
    
    # if (Nci.objects.filter(choice="Re-attempt").exists()) | (Nci.objects.filter(choice="Return").exists()):
    #     active_nci=Nci.objects.filter(choice="Re-attempt")| Nci.objects.filter(choice="Return")
    #     return render(request, 'admin_dashboard.html',{'active_nci': active_nci} )
  # if (Nci.objects.filter(choice="Re-attempt").exists()) | (Nci.objects.filter(choice="Return").exists()):
    #     cn_list=[]
    #     all_nci=Nci.objects.all()
    #     for i in range(len(all_nci)):
    #         if all_nci[i].cn_number not in cn_list:
    #             cn_list.append(all_nci[i].cn_number)
    #     active_nci=[]
    #     for i in range(len(cn_list)):
    #         if (all_nci.filter(cn_number=cn_list[i]).last().choice == 'Re-attempt') | (all_nci.filter(cn_number=cn_list[i]).last().choice == 'Return'):
    #             active_nci.append(all_nci[i])
    #     return render(request, 'admin_dashboard.html',{'active_nci': active_nci} )
    
    if (Nci.objects.filter(choice='Re-attempt').exists()) | (Nci.objects.filter(choice='Return').exists()):
        active_nci=Nci.objects.all()
        return render(request, 'admin_dashboard.html',{'active_nci': active_nci} )
    else:
        msg="No Record Found !"
        return render(request, 'admin_dashboard.html', {'msg': msg} )





def get_total_reattempts(request):
    ## IMPORTANT
    # active status is actually inactive for admin unlike user
    # inactive status is actually active for admin unlike user
    all_nci=Nci.objects.all()
    cn_list=[]
    username_list=[]
    total_active_nci=[]
    for i in range(len(all_nci)):
        if all_nci[i].cn_number not in cn_list:
            cn_list.append(all_nci[i].cn_number)
        # if all_nci[i].username not in username_list:
            username_list.append(all_nci[i].username)
    
    for i in range(len(cn_list)):
        total_active_nci.append(len(all_nci.filter(cn_number=cn_list[i], choice="Re-attempt")))

    list_active_nci={
        'cn_list':cn_list, 
        'username_list':username_list,
        'total_active_nci':total_active_nci
    }
    active_nci_list=[]
    for j in range(len(cn_list)):
        active_nci_list.append([cn_list[j], username_list[j], total_active_nci[j]])

    print(active_nci_list)
    return render(request, 'admin_dashboard.html' , {'list_active_nci':active_nci_list})


def change_nci_status(request):
    cn_number=request.POST['cn_number']
    # name=request.POST['name']
    mobile_number=request.POST['mobile_number']
    address=request.POST['address']
    choice=request.POST['choice']
    change_status=request.POST['change_status']
    # print("CHanging :  "+cn_number+" "+mobile_number+" "+address+" "+choice+"-->to-->"+change_status)
    change_nci_status=Nci.objects.get(cn_number=cn_number, mobile_number=mobile_number,address=address, choice=choice)
    change_nci_status.status=change_status
    change_nci_status.save()
    print("CHanging :  "+cn_number+" "+mobile_number+" "+address+" "+choice+"-->to-->"+change_nci_status.status)

    return render(request, 'admin_dashboard.html')


def bulk_booking(request):
    last_cn_num=int(request.POST['cn_number'])
    booking_file=request.FILES['booking_file']
    df=pd.read_excel(booking_file)
    noOfBookings=df['Shipper_Username'].count()
    
    # Check if Username is Wrong in the File


    product_in_file=df['Product']
    pieces_in_file=df['Pieces']
    successfull_booking_cn_numbers=[]
    for i in range(noOfBookings):
        if Customer.objects.filter(username=df['Shipper_Username'][i]).exists():
            separate_product=[]
            separate_pieces=[]
            if "," in product_in_file[i]:
                if "," not in str(pieces_in_file[i]):
                    messages.info(request, 'May be you forgot to put "," in the File in "Pieces" Column! ')
                    return render(request, 'user_dashboard.html')
                else:
                    for j in range(len(product_in_file[i].split(","))):
                        separate_product.append(product_in_file[i].split(",")[j].lstrip())
                        separate_pieces.append(pieces_in_file[i].split(",")[j].lstrip())
            else:
                separate_product.append(product_in_file[i])
                separate_pieces.append(pieces_in_file[i])

            
            for k in range(len(separate_product)):
                if Product.objects.filter(username=df['Shipper_Username'][0], product_description=separate_product[k]).exists():
                    pass
                    # print("USER, Product and Pieces Verfied!: ",separate_product[k]+"  ",separate_pieces[k])

                else:
                    messages.info(request, 'Wrong Product in File ')
                    return render(request, 'user_dashboard.html')

            cn_number=last_cn_num
            username=df['Shipper_Username'][i]
            name=df['Consignee_Name'][i]
            mobile_number=df['Consignee_Mobile_Number'][i]
            email=df['Email'][i]
            destination_city=df['Destination_City'][i]
            address=df['Address'][i]
            default_origin_city=df['Default_Origin_City'][i]
            weight=df['Weight'][i]
            pieces=df['Pieces'][i]
            customer_reference_number=df['Customer_Reference_Number'][i]
            service_type=df['Service_Type'][i]
            flyer_number=df['Flyer_Number'][i]
            special_handling=df['Special_Handling'][i]
            product_detail=df['Product'][i]
            cash_amount=df['Cash_Amount'][i]
            pickup_city=df['Pickup_City'][i]
            manual=df['Manual'][i]
            status="Booked"

            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            dt_string = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
            dt_string = dt_string + timedelta(hours=5)
            dateTime=dt_string
            successfull_booking_cn_numbers.append(perform_Booking(separate_product,separate_pieces, cn_number, username, name, mobile_number, email, destination_city, address, default_origin_city, weight, pieces, customer_reference_number, service_type, flyer_number, special_handling, product_detail, cash_amount, pickup_city, status, dateTime, manual))
            last_cn_num+=1
        else:
            messages.info(request, 'Wrong Username in File !!! ')
            return render(request, 'user_dashboard.html')


    
    messages.info(request, 'Booking Done Successfully with CN Numbers ', successfull_booking_cn_numbers)
    return render(request, 'user_dashboard.html')


def perform_Booking(separate_product,separate_pieces,cn_number, username, name, mobile_number, email, destination_city, address, default_origin_city, weight, pieces, customer_reference_number, service_type, flyer_number, special_handling, product_detail, cash_amount, pickup_city, status, dateTime, manual):
    print("************************ RECEIVED DATA*********************************")
    # print(cn_number, username, name, mobile_number, email, destination_city, address, default_origin_city, weight, pieces, customer_reference_number, service_type, flyer_number, special_handling, product_detail, cash_amount, pickup_city, status, dateTime)
    print("LENGTH OF PROD: ", len(separate_product))

    for i in range(len(separate_product)):
        updateQuant=Product.objects.get(username=username, product_description=separate_product[i])
        print("PREVIOUSLY:------------   ")
        print(updateQuant.quantity_available, "   ", updateQuant.quantity_in_process)
        
        
        updateQuant.quantity_available-=int(separate_pieces[i])
        updateQuant.quantity_in_process+=int(separate_pieces[i])
        print("After:------------   ")
        print(updateQuant.quantity_available, "   ", updateQuant.quantity_in_process)
        updateQuant.save()
    
    rec=BookingLog.objects.last().record_no
    rec+=1
    booking= BookingLog.objects.create(record_no=rec, cn_number=cn_number, username=username,  name=name, mobile_number=mobile_number, email=email, destination_city=destination_city, address=address, default_origin_city=default_origin_city, weight=weight, pieces=pieces,customer_reference_number=customer_reference_number,service_type=service_type, flyer_number=flyer_number, special_handling=special_handling , product_detail=product_detail,cash_amount=cash_amount,pickup_city=pickup_city, status=status, dateTime=dateTime, manual=manual )
    booking.save()
    return cn_number


def change_status_of_selected_bookings(request):
    newStatus=request.POST['status']
    cn_nums=request.POST['cn_nums']
    # print(cn_nums)  # This String is in rough Form' 45900000004 ,  45900000006 ,'
    cn_list=[]
    cn_list=cn_nums.split(', ')
    for i in range(len(cn_list)):
        if ',' in cn_list[i]:
            cn_list[i]=cn_list[i].replace(',', '')
        cn_list[i]=cn_list[i].lstrip()
        cn_list[i]=cn_list[i].rstrip()
    cn_list=cn_list[:-1]
    # print(cn_list) # Now cn numbers are in list in fine form
    # print("Changing ", cn_list, " to "+ newStatus) 
    for i in range(len(cn_list)):
        # print("TOTAL CN NUMBS ARE : ", len(cn_list))
        record=BookingLog.objects.filter(cn_number=cn_list[i]).last()
        username=record.username
        name=record.name
        mobile_number=record.mobile_number
        email=record.email
        destination_city=record.destination_city
        address=record.address
        default_origin_city=record.default_origin_city
        weight=record.weight
        piecess=record.pieces
        customer_reference_number=record.customer_reference_number
        service_type=record.service_type
        flyer_number=record.flyer_number
        special_handling=record.special_handling
        product_detail=record.product_detail
        cash_amount=record.cash_amount
        pickup_city=record.pickup_city
        manual=record.manual
        status=newStatus
        
        
        now = datetime.now()
            # dd-mm-YY H:M:S
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        dt_string = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        dt_string = dt_string + timedelta(hours=5)
        
        rec=BookingLog.objects.last().record_no
        rec+=1

        new_rec= BookingLog.objects.create(record_no=rec, cn_number=cn_list[i], username=username,  name=name, mobile_number=mobile_number, email=email, destination_city=destination_city, address=address, default_origin_city=default_origin_city, weight=weight, pieces=piecess,customer_reference_number=customer_reference_number,service_type=service_type, flyer_number=flyer_number, special_handling=special_handling , product_detail=product_detail,cash_amount=cash_amount,pickup_city=pickup_city, status=status, dateTime=dt_string, manual=manual )
        new_rec.save()
        print("Changed ", cn_list[i], " to "+ newStatus) 
        

    return render(request, 'admin_dashboard.html')

    
def add_1_day_to_date(c):
    d=int(c[-2:])
    m=int(c[5:7])
    y=int(c[:4])
    leapYear=False
    if y % 4 == 0:
        leapYear=True
    mo_31=[1,3,5,7,8,10,12]
    mo_30=[4,6,9,11]
    mo_feb=[2]
    if m in mo_31:
        if d==31:
            d=1
            if m!=12:
                m+=1
            else:
                y+=1
                m=1
        else:
            d+=1
    elif m in mo_30:
        if d==30:
            d=1
            m+=1
        else:
            d+=1
    else:
        if leapYear == False:
            if d==28:
                d=1
                m+=1
            else:
                d+=1
        else:
            if d==29:
                d=1
                m+=1
            else:
                d+=1
    z="0"
    if len(str(d))==1:
        d=z+str(d)
    if len(str(m))==1:
        m=z+str(m)
    m=str(m)
    d=str(d)
    y=str(y) 
    to_date=y+"-"+m+"-"+d
    return to_date


def filter_bookings_date_wise(username, from_date, to_date):
    pass
    

def compare_username_with_extension_of_booking_id(username):
    if username=="BASKETMOMbERFF-688":
        return "bomb"
    elif username=='AStoreByIbtasam//Ff-482':
        return "ibts"
    elif username=='BLACKGOLD-FF-508':
        return "gold"
    elif username=='hassan-ff-108':
        return "savy"
    elif username=='FitsBurry-ff-852':
        return 'fits'
    elif username=='kidcareFF-742':
        return 'kids'
    elif username=='Elvepk-FF-874':
        return 'elve'
    elif username=='pollycosmeticff-687':
        return 'poly'
    elif username=='PERFETTOFF-468':
        return 'perf'
    elif username=='HealthOrganizer-ff-325':
        return 'heal'
    elif username=='LEMAORGANICS-FF-708':
        return 'lema'
    elif username=='Shakamobile-ff-857':
        return 'shak'
    elif username=='zotics-ff-868':
        return 'zoti'
    elif username=='BotanicalGardenbyM.ff 818':
        return 'bota'
 

def searchDateWise2(request):
    username=request.POST['username']
    status=request.POST['status']
    from_date=request.POST['from_date']
    # c=request.POST['to_date']
    # to_date=add_1_day_to_date(c)
    to_date=request.POST['to_date']
    extension=compare_username_with_extension_of_booking_id(username)
  
    #USING LEAPORD API FOR EXTRACTING DATA USING TIME RANGE      
    querystring = {
        'api_key' : 'D8C01F4A1E2115914D0A7D20369B2644',
        'api_password' : 'HUSNAIN1@1',
        'from_date' : from_date,
        'to_date' : to_date  
    }
    url='http://new.leopardscod.com/webservice/getBookedPacketLastStatus/format/json/?'
    r=requests.get(url, params=querystring).json()
    # print(r)
    rec_received_from_api=[]

    if r['error']==0: # NO ERROR
        length_of_data_received=len(r['packet_list'])
        for i in range(length_of_data_received):
            if r['packet_list'][i]['booked_packet_order_id'][:4]==extension:
                rec_received_from_api.append(r['packet_list'][i])
        
        all_bookings_in_this_range=[]
        for i in range(len(rec_received_from_api)):
        
            if BookingLog.objects.filter(customer_reference_number=rec_received_from_api[i]['booked_packet_order_id']).exists():
                cn_num=BookingLog.objects.filter(customer_reference_number=rec_received_from_api[i]['booked_packet_order_id']).last().cn_number
                cons_name=BookingLog.objects.filter(customer_reference_number=rec_received_from_api[i]['booked_packet_order_id']).last().name
                mob_num=BookingLog.objects.filter(customer_reference_number=rec_received_from_api[i]['booked_packet_order_id']).last().mobile_number
                product=BookingLog.objects.filter(customer_reference_number=rec_received_from_api[i]['booked_packet_order_id']).last().product_detail
                cash=BookingLog.objects.filter(customer_reference_number=rec_received_from_api[i]['booked_packet_order_id']).last().cash_amount
                status1=rec_received_from_api[i]['booked_packet_status']
                temp=BookingLog.objects.filter().first()
                temp.cn_number=cn_num
                temp.name=cons_name
                temp.mobile_number=mob_num
                temp.product_detail=product
                temp.cash_amount=cash
                temp.status=status1
                if status=='All Bookings':
                    all_bookings_in_this_range.append(temp)
                elif (status=='Delivered')&(status1=='Delivered'):
                    all_bookings_in_this_range.append(temp)
                elif (status=='Booked')&(status1=='Pickup Request not Send'):
                    all_bookings_in_this_range.append(temp)
                elif (status=="Returned to Shipper")&(status1=='Returned to shipper'):
                    all_bookings_in_this_range.append(temp)
                elif (status=="In-Transit")&((status1!='Delivered')&(status1!='Returned to shipper')&(status1!='Pickup Request not Send')):
                    all_bookings_in_this_range.append(temp)
                else:
                    pass

        if all_bookings_in_this_range==[]:
            messages.info(request, "No record Found!")
            return render(request, 'user_dashboard.html')
        else:
            return render(request, 'user_dashboard.html',{'all_bookings': all_bookings_in_this_range} )
    else:
        messages.info(request, "No record Found!")
        return render(request, 'user_dashboard.html')

    # messages.info(request, "In Maintainance Process!")
    return render(request, 'user_dashboard.html')


# return render(request, 'user_dashboard.html',{'all_bookings': this_rec} )


    # Returned to shipper


def getAge(request):
    cn_numbers=request.POST['cn_numbers']
    cn_list=[]
    cn_list=cn_numbers.split(', ')
    for i in range(len(cn_list)):
        if ',' in cn_list[i]:
            cn_list[i]=cn_list[i].replace(',', '')
        cn_list[i]=cn_list[i].lstrip()
        cn_list[i]=cn_list[i].rstrip()
    cn_list=cn_list[:-1]
    extracted_cn_num=int(cn_list[0])

    booking_id=BookingLog.objects.filter(cn_number=extracted_cn_num).last().customer_reference_number
    
    # LEAPARD API For GETTING DATA USING ORDER ID
    url = "http://new.leopardscod.com/webservice/getShipmentDetailsByOrderID/format/json/"
    headerz = {
        "content-type": "application/json"
    }
    # API KEY and Password
    API_KEY = "D8C01F4A1E2115914D0A7D20369B2644"
    API_PASSWORD="HUSNAIN1@1"
    # Order Id(s)
    SHIPMENT_ID= []
    SHIPMENT_ID.append(booking_id)
    # SHIPMENT_ID=json.dumps(SHIPMENT_ID)
    querystring = {
        'api_key' : API_KEY,
        'api_password' : API_PASSWORD,
        'shipment_order_id' : SHIPMENT_ID
    }
    r = requests.post(url = url, json=querystring, headers=headerz )
    output = r.json()
    if output['error']!="":
        return JsonResponse({'cn_age':'none'}) # NO such booking order id in Leapard
    else:
        if len(output['data'])>1:
            return JsonResponse({'cn_age':'Conflicting'}) # More than 1 bookings with this order id
        else:
            from_date=str(output['data'][0]['booking_date'])+" 08:00:00"
            
            to_date=""
            if output['data'][0]['booked_packet_status']=='Delivered':  
                to_date=str(output['data'][0]['delivery_date'])+" 08:00:00"
            elif output['data'][0]['booked_packet_status']=='Returned to shipper':
                to_date=str(output['data'][0]['return_date'])
            else:
                now = datetime.now()
            
                dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
                dt_string = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
                dt_string = dt_string + timedelta(hours=5)
                to_date=str(dt_string)
            from_date=datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S' )
            to_date=datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S' )
            # print(from_date, to_date)
            # messages.info(request, str(from_date)+" "+str(to_date))
            age=to_date-from_date
            # messages.info(request, "Age is ", age.days)
    
            return JsonResponse({'cn_age':age.days})