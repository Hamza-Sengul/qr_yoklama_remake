from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='student_login'),
    path('register/', views.register_view, name='student_register'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'), 
    path('submit-qr/', views.submit_qr, name='submit_qr'),
    path('logout/', views.logout_view, name='logout'), 
    path('gecmis-yoklamalar/', views.gecmis_yoklamalar, name='gecmis_yoklamalar'),
    path('devamsizlik-durumu/', views.devamsizlik_durumu, name='devamsizlik_durumu'),
]
