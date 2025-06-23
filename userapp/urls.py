from django.contrib import admin
from django.urls import path,include
from userapp import views as views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('about/',views.about,name='about'),
    
    path('contact/',views.contact,name='contact'),
    path('register/',views.user_register,name='user_register'),
    
    path('login/', views.user_login, name='user_login'),
    path('otp/', views.user_otp, name='user_otp'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path("logout/",views.user_logout,name="user_logout"),



    path("pdf/",views.pdf_upload,name="pdf"),
    path('extract/', views.extract_text_from_files, name='extract_text_from_files'),
    path('chat/', views.chat_invoice, name='chat_invoice'),
    path("profile/", views.user_profile,name="user_profile"),
    path("history/", views.history,name="history"),
    path('download_invoice/', views.download_invoice, name='download_invoice'), 
    path('share_invoice/<int:invoice_id>/', views.share_invoice, name='share_invoice'),




      
                   
]