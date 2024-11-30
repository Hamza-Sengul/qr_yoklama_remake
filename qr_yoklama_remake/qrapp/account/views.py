from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import QRData, Attendance
from django.contrib.auth import logout
from django.core.paginator import Paginator

def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Başarıyla giriş yaptınız.")
            return redirect('student_dashboard')  # Giriş sonrası yönlendirme
        else:
            messages.error(request, "E-posta veya şifre hatalı.")
    
    return render(request, 'student_login.html')

def register_view(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Şifreler eşleşmiyor.")
            return redirect('student_register')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, "Bu e-posta ile bir hesap zaten mevcut.")
            return redirect('student_register')
        
        user = User.objects.create_user(
            username=email,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        messages.success(request, "Kayıt işlemi başarılı! Giriş yapabilirsiniz.")
        return redirect('student_login')
    
    return render(request, 'student_register.html')

def logout_view(request):
    logout(request)  # Kullanıcının oturumunu kapat
    return redirect('student_login') 

def student_dashboard(request):
    yoklamalar = QRData.objects.filter(user=request.user).order_by('-date_time')
    paginator = Paginator(yoklamalar, 5)
    page_number = request.GET.get('page', 1)  # 'page' parametresinden sayfa numarasını al
    page_obj = paginator.get_page(page_number)
    return render(request, 'student_dashboard.html', {'page_obj': page_obj})

@csrf_exempt
def submit_qr(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_content = data.get('qr_content')

            if not qr_content:
                return JsonResponse({'status': 'error', 'message': 'QR içeriği eksik.'}, status=400)

            user = request.user
            if not user.is_authenticated:
                return JsonResponse({'status': 'error', 'message': 'Kullanıcı oturum açmamış.'}, status=401)

            # QR kodun daha önce kaydedilip kaydedilmediğini kontrol et
            existing_record = QRData.objects.filter(user=user, qr_content=qr_content).exists()
            if existing_record:
                return JsonResponse({'status': 'warning', 'message': 'Bu yoklama zaten alınmış.'}, status=200)

            # Yeni QR kodu kaydet
            QRData.objects.create(
                user=user,
                qr_content=qr_content,
                additional_info=f"Kullanıcı: {user.first_name} {user.last_name}, E-posta: {user.email}"
            )

            return JsonResponse({'status': 'success', 'message': 'Yoklama başarı ile alındı.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'}, status=400)

def gecmis_yoklamalar(request):
    # Kullanıcının geçmiş yoklamalarını al
    yoklamalar = QRData.objects.filter(user=request.user).order_by('-date_time')
    
    # Sayfalama işlemi (her sayfada 5 kayıt gösterilecek)
    paginator = Paginator(yoklamalar, 10)
    page_number = request.GET.get('page', 1)  # 'page' parametresinden sayfa numarasını al
    page_obj = paginator.get_page(page_number)

    return render(request, 'gecmis_yoklamalar.html', {'page_obj': page_obj})


def devamsizlik_durumu(request):
    attendance = Attendance.objects.filter(user=request.user)
    return render(request, 'devamsizlik_durumu.html', {'attendance': attendance})
