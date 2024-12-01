from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import QRData, Attendance, QRCode, Course, CourseStudent
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from io import BytesIO
import qrcode
from django.core.files.base import ContentFile
import base64
from .forms import CreateCourseForm, AddStudentForm
from functools import wraps

def is_academic(user):
    return user.is_staff

def academic_required(view_func):
    @user_passes_test(is_academic, login_url='login', redirect_field_name=None)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper

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

            # Kullanıcının e-posta adresinden okul numarasını al
            email = user.email
            school_number = email.split('@')[0]

            # QR kod daha önce okutulmuş mu?
            existing_record = QRData.objects.filter(user=user, qr_content=qr_content).exists()
            if existing_record:
                return JsonResponse({'status': 'warning', 'message': 'Bu yoklama zaten alınmış.'}, status=200)

            # Kullanıcının kayıtlı olduğu dersler
            enrolled_courses = Attendance.objects.filter(user=user)
            if not enrolled_courses.exists():
                return JsonResponse({'status': 'error', 'message': 'Herhangi bir derse kayıtlı değilsiniz.'}, status=400)

            # QR içeriği derslerden herhangi biriyle eşleşiyor mu?
            matched_course = None
            for course in enrolled_courses:
                course_keywords = course.course_name.lower().split()  # Ders adını anahtar kelimelere ayır
                if all(keyword in qr_content.lower() for keyword in course_keywords):
                    matched_course = course
                    break

            if not matched_course:
                return JsonResponse({
                    'status': 'error',
                    'message': 'QR kod içeriği kayıtlı olduğunuz derslerle uyuşmuyor.'
                }, status=400)

            # Yoklama kaydı oluştur veya güncelle
            if matched_course.absences < matched_course.max_absences:
                matched_course.absences = max(0, matched_course.absences - 1)
                matched_course.save()

            # QR verisini veritabanına kaydet
            QRData.objects.create(
                user=user,
                qr_content=qr_content,
                school_number=school_number,
                additional_info=f"Kullanıcı: {user.first_name} {user.last_name}, E-posta: {email}"
            )

            return JsonResponse({'status': 'success', 'message': f"{matched_course.course_name} için yoklama başarıyla alındı."})
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


def academic_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Şifreler eşleşmiyor!")
            return redirect('academic_register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu e-posta adresi zaten kayıtlı.")
            return redirect('academic_register')

        user = User.objects.create_user(
            username=email,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_staff=True  # Akademisyen olarak işaretle
        )
        messages.success(request, "Kayıt işlemi başarılı! Giriş yapabilirsiniz.")
        return redirect('academic_login')
    
    return render(request, 'academic_register.html')

# Akademisyen giriş
def academic_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user and user.is_staff:
            login(request, user)
            messages.success(request, f"Hoşgeldiniz, {user.first_name}!")
            return redirect('academic_dashboard')
        else:
            messages.error(request, "E-posta veya şifre hatalı ya da yetkiniz yok.")
            return redirect('academic_login')

    return render(request, 'academic_login.html')

# Akademisyen çıkış
def academic_logout(request):
    logout(request)
    messages.success(request, "Başarıyla çıkış yaptınız.")
    return redirect('academic_login')


@academic_required
def academic_dashboard(request):
    academic_user = request.user
    courses = Course.objects.filter(academic_user=academic_user)
    return render(request, 'academic_dashboard.html', {'academic_user': academic_user, 'courses': courses})



@login_required
def view_students(request):
    academic_user = request.user
    courses = Course.objects.filter(academic_user=academic_user).prefetch_related('students__student')
    students = Attendance.objects.filter(course_name="Algoritma ve Programlama")
    return render(request, 'view_students.html', {'students': students, 'courses': courses})

def create_qr_code_view(request):
    if request.method == "POST":
        course_name = request.POST.get("course_name")
        week_info = request.POST.get("week_info")

        # QR kod içeriği oluştur
        qr_content = f"{course_name} - {week_info}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_content)
        qr.make(fit=True)

        # QR kod görselini oluştur
        img = qr.make_image(fill="black", back_color="white")

        # Görseli hafızada tut (BytesIO)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Görseli base64 formatına çevir
        qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # QR kodu tabloya kaydetme (opsiyonel)
        QRCode.objects.create(
            academic_user=request.user,
            course_name=course_name,
            week_info=week_info,
        )

        return render(request, "create_qr_code.html", {"qr_image_base64": qr_image_base64})

    return render(request, "create_qr_code.html")


@login_required
def create_course(request):
    if request.method == 'POST':
        form = CreateCourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.academic_user = request.user  # Oturum açan akademisyenle ilişkilendir
            course.save()
            messages.success(request, f"Ders '{course.name}' başarıyla oluşturuldu.")
            return redirect('academic_dashboard')
    else:
        form = CreateCourseForm()

    return render(request, 'create_course.html', {'form': form})



@login_required
def add_student(request):
    # Sadece oturum açan akademisyenin derslerini getirin
    courses = Course.objects.filter(academic_user=request.user)
    students = User.objects.exclude(courses__academic_user=request.user)

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        selected_students = request.POST.getlist('selected_students')  # Toplu öğrenci seçimi
        email = request.POST.get('email')  # E-posta ile ekleme

        try:
            # Sadece kendi dersi üzerinde işlem yapabilmesi için kontrol
            course = Course.objects.get(id=course_id, academic_user=request.user)

            if selected_students:
                for student_id in selected_students:
                    student = User.objects.get(id=student_id)
                    if CourseStudent.objects.filter(course=course, student=student).exists():
                        messages.warning(request, f"{student.first_name} {student.last_name} zaten {course.name} dersine kayıtlı.")
                    else:
                        CourseStudent.objects.create(course=course, student=student)
                        messages.success(request, f"{student.first_name} {student.last_name} başarıyla {course.name} dersine eklendi.")
            elif email:
                student = User.objects.get(email=email)
                if CourseStudent.objects.filter(course=course, student=student).exists():
                    messages.warning(request, f"{student.first_name} {student.last_name} zaten {course.name} dersine kayıtlı.")
                else:
                    CourseStudent.objects.create(course=course, student=student)
                    messages.success(request, f"{student.first_name} {student.last_name} başarıyla {course.name} dersine eklendi.")
        except User.DoesNotExist:
            messages.error(request, "Bu e-posta adresine sahip bir öğrenci bulunamadı.")
        except Course.DoesNotExist:
            messages.error(request, "Seçilen ders bulunamadı.")

        return redirect('add_student')

    return render(request, 'add_student.html', {
        'students': students,
        'courses': courses,
    })