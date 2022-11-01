# from asyncio.windows_events import NULL
from contextlib import nullcontext
# import email
from datetime import datetime
from multiprocessing.sharedctypes import Value
from pprint import pprint
import statistics
from xmlrpc.client import DateTime
from django.shortcuts import render, redirect
import imp
from django.shortcuts import render
from django.http import HttpResponse
from myapp2.models import Booking, BookingLog, Customer
from .booking_form import BookingForm
from .models import Product
from .ProductForm import ProductForm
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponseRedirect
import random
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
                cust_id= round(random.random()*1000000)
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
                cust_id= round(random.random()*1000000)
                # booking_no=0
                # booking_no=str(booking_no).zfill(5)
                # consignment_no=(str(cust_id)+booking_no)
                # consignment_no=int(consignment_no)
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
            if username == 'admin':
                total_bookings=len(BookingLog.objects.filter(status="Booked"))
                total_delivered_bookings=len(BookingLog.objects.filter( status='Delivered'))
                total_returned_bookings=len(BookingLog.objects.filter( status='Returned to Shipper'))
                stats={
                    'total_bookings':total_bookings,
                    'total_delivered_bookings':total_delivered_bookings,
                    'total_returned_bookings':total_returned_bookings,
                    'delivery_rate':round((total_delivered_bookings/total_bookings)*100,2),
                    'return_rate':round(total_returned_bookings/total_bookings, 2)
                }
                return render(request, 'admin_dashboard.html',stats)
    
            else:
                if BookingLog.objects.filter(username=username).exists():
                    total_bookings=len(BookingLog.objects.filter(username=username, status="Booked"))
                    total_delivered_bookings=len(BookingLog.objects.filter(username=username, status='Delivered'))
                    total_returned_bookings=len(BookingLog.objects.filter(username=username, status='Returned to Shipper'))
                    stats={
                        'total_bookings':total_bookings,
                        'total_delivered_bookings':total_delivered_bookings,
                        'total_returned_bookings':total_returned_bookings,
                        'delivery_rate':round((total_delivered_bookings/total_bookings)*100,2),
                        'return_rate':round(total_returned_bookings/total_bookings, 2)
                    }
                else:
                    stats={
                        'total_bookings':0,
                        'total_delivered_bookings':0,
                        'total_returned_bookings':0,
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
        m=int((len(request.POST.keys())-14)/2)
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
        now = datetime.now()
        # dd-mm-YY H:M:S
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

        rec=BookingLog.objects.last().record_no
        rec+=1
        booking= BookingLog.objects.create(record_no=rec, cn_number=cn_number, username=username,  name=name, mobile_number=mobile_number, email=email, destination_city=destination_city, address=address, default_origin_city=default_origin_city, weight=weight, pieces=pieces,customer_reference_number=customer_reference_number,service_type=service_type, flyer_number=flyer_number, special_handling=special_handling , product_detail=product_detail,cash_amount=cash_amount,pickup_city=pickup_city, status=status, dateTime=dt_string )
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
                cust_id= round(random.random()*1000000)
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
    status=updated_status
    
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    dateTime=dt_string
    
    rec=BookingLog.objects.last().record_no
    rec+=1

    new_rec= BookingLog.objects.create(record_no=rec, cn_number=cn_num, username=username,  name=name, mobile_number=mobile_number, email=email, destination_city=destination_city, address=address, default_origin_city=default_origin_city, weight=weight, pieces=piecess,customer_reference_number=customer_reference_number,service_type=service_type, flyer_number=flyer_number, special_handling=special_handling , product_detail=product_detail,cash_amount=cash_amount,pickup_city=pickup_city, status=status, dateTime=dateTime )
    new_rec.save()

    # n_product=request.POST['product_description']
    # n_pieces=request.POST['pieces']

    if ',' in str(piecess):
        piec=piecess.split(", ")
        prod=product_detail.split(", ")
    else:
        piec=[piecess]
        prod=[product_detail]
        print("**************************************")
        print(piec)
        print(prod)
    if Product.objects.filter(username=username):
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
        
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    



#     last_data=Booking.objects.last()
    
#     if Booking.objects.filter(cn_number=last_data.cn_number).exists():
#         # print("*********************** ", last_data.cn_number)
#         # all_bookings=Booking.objects.all()
#         all_bookings={'book':last_data}
#         # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",all_bookings['book'].cn_number)
#         return render(request, 'after_booking.html', {'all_bookings': last_data})
        
#     else:
#         print("*********************** NOT DONE *********************")



def delete_booking(request):
    cn_number=request.POST['cn_number']
    statu=request.POST['statu']
    if statu=='Picked':
        statu+=' by FulfillKaro'
    elif statu=='Packed':
        statu+=' by FulfillKaro'
    elif statu=='Prepared':
        statu+=' for Movement to Destination City'
    elif statu=='Arrival':
        statu+=' at Origin'
    elif statu=='Physically':
        statu+=' Loaded for movement to Destination City'
    elif statu=='Loading':
        statu+=' for Return to Shipper'
    elif statu=='Returned':
        statu+=' to Shipper'
    elif statu=='On':
        statu+=' the Way to be Deivered'
    elif statu=='Refused':
        statu+=' by Customer'
    elif statu=='Loaded':
        statu+=' for Return to Shipper'
    elif statu=='Refused':
        statu+=' by Customer'

                
    print("____________________________")
    print(cn_number,"   "+ statu )
    member = BookingLog.objects.filter(cn_number=cn_number, status=statu).last()
    member.delete()
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


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
            'delivery_rate':round((total_delivered_bookings/total_bookings)*100, 2),
            'return_rate':round(total_returned_bookings/total_bookings, 2)
        }
        return render(request, 'admin_dashboard.html',stats)
    else:
        if BookingLog.objects.filter(username=username).exists():
            total_bookings=len(BookingLog.objects.filter(username=username, status="Booked"))
            total_delivered_bookings=len(BookingLog.objects.filter(username=username, status='Delivered'))
            total_returned_bookings=len(BookingLog.objects.filter(username=username, status='Returned to Shipper'))
            stats={
                'total_bookings':total_bookings,
                'total_delivered_bookings':total_delivered_bookings,
                'total_returned_bookings':total_returned_bookings,
                'delivery_rate':round((total_delivered_bookings/total_bookings)*100,2),
                'return_rate':round(total_returned_bookings/total_bookings, 2)
            }
        else:
            stats={
                'total_bookings':0,
                'total_delivered_bookings':0,
                'total_returned_bookings':0,
                'delivery_rate':0,
                'return_rate':0.0
        }
        return render(request, 'user_dashboard.html',stats)



def getLog(request):
    cn_number=request.POST['cn_number']
    bookings_log=BookingLog.objects.filter(cn_number=cn_number)
    # return redirect('/', {'all_bookings':all_bookings} )
  
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
    from_date=request.POST['from_date']
    # to_date=request.POST['to_date']
    c=request.POST['to_date']
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


    username=request.POST['username']
    rec=BookingLog()
    if username=="admin":
        rec=BookingLog.objects.filter(dateTime__range=[from_date, to_date])
    else:     
        rec=BookingLog.objects.filter(username=username, dateTime__range=[from_date, to_date])
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
            # return render(request, 'admin_dashboard.html')
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        else:
            messages.info(request, "No Record in this Time Range !!!")
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            # return render(request, 'user_dashboard.html')
    else:
        if username=="admin":
            return render(request, 'admin_dashboard.html',{'all_bookings': filtered_rec} )
        else:
            return render(request, 'user_dashboard.html',{'all_bookings': filtered_rec} )



# def showDetail(request):
    # from_date=request.POST['from_date']
    # to_date=request.POST['to_date']
    # username=request.POST['username']
    # rec=BookingLog.objects.filter(username=username, dateTime__range=[from_date, to_date])
    # # print(username, "***************************"+from_date+"*********************"+to_date+"*********** Total records in this time range: ", len(rec))
    # # *"+rec[0].dateTime+"******"+rec[1].dateTime)
    # return render(request, 'user_dashboard.html',{'all_bookings': rec} )



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

    for i in range (len(all_u)):
        # print("********************* User ", (i+1), " ************")
        context['username'].append(all_u[i].username)
                
        # print("Username: "+all_u[i].username)
        if Customer.objects.filter(username=all_u[i].username).exists():
            customer_id=Customer.objects.get(username=all_u[i].username).customer_id
            context['customer_id'].append(customer_id)
            # print("Customer Id: ",customer_id)
    return render(request, 'admin_dashboard.html', {'context':context} )

    