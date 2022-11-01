from django.urls import path
from . import views
urlpatterns=[
    path('', views.index, name='index'),
    path('after_booking', views.after_booking, name="after_booking"),
    path('show_bookings', views.show_bookings, name="show_bookings"),
    path('done_booking', views.done_booking, name="done_booking"),
    path('menu', views.menu, name="menu"),
    path('delete_booking', views.delete_booking, name="delete_booking"),
    path('register', views.register, name="register"),
    path('register', views.register, name="register"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('lastbooking', views.lastbooking, name="lastbooking"),
    path('goto_home', views.goto_home, name="goto_home"),
    path('save_changes', views.save_changes, name="save_changes"),
    path('getStatistics', views.getStatistics, name="getStatistics"),
    path('searchRecord', views.searchRecord, name="searchRecord"),
    path('get_last', views.get_last, name="get_last"),
    path('cancelRecord', views.cancelRecord, name="cancelRecord"),
    path('getLog', views.getLog, name="getLog"),
    path('searchDateWise', views.searchDateWise, name="searchDateWise"),
    path('showProduct', views.showProduct, name="showProduct"),
    path('goto_Product_Page', views.goto_Product_Page, name="goto_Product_Page"),
    path('save_stock_record', views.save_stock_record, name="save_stock_record"),
    path('showProducts', views.showProducts, name="showProducts"),
    path('editProduct', views.editProduct, name="editProduct"),
    path('showAllCustomers', views.showAllCustomers, name="showAllCustomers"),
    
    ]