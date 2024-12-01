from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_view, name='student_login'),
    path('register/', views.register_view, name='student_register'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'), 
    path('submit-qr/', views.submit_qr, name='submit_qr'),
    path('logout/', views.logout_view, name='logout'), 
    path('gecmis-yoklamalar/', views.gecmis_yoklamalar, name='gecmis_yoklamalar'),
    path('devamsizlik-durumu/', views.devamsizlik_durumu, name='devamsizlik_durumu'),
    path('academic/register/', views.academic_register, name='academic_register'),
    path('academic/login/', views.academic_login, name='academic_login'),
    path('academic/logout/', views.academic_logout, name='academic_logout'),
    path('academic/dashboard/', views.academic_dashboard, name='academic_dashboard'),
    path("create-qr/", views.create_qr_code_view, name="create_qr"),
    path('academic/view-students/', views.view_students, name='view_students'),
    path('academic/create-course/', views.create_course, name='create_course'),
    path('academic/add-student/', views.add_student, name='add_student'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
