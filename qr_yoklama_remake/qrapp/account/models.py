from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings

class QRData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="qr_records")
    qr_content = models.TextField()  # QR kod içeriği
    school_number = models.CharField(max_length=20, blank=True, null=True)  # Okul numarası
    date_time = models.DateTimeField(default=now)  # Tarih ve zaman
    additional_info = models.TextField(blank=True, null=True)  # QR ile gelen ek bilgi

    def __str__(self):
        return f"{self.user.first_name} - {self.qr_content} - {self.school_number}"

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    course_name = models.CharField(max_length=255)  # Ders adı
    total_weeks = models.IntegerField(default=14)  # Toplam hafta sayısı
    absences = models.IntegerField(default=0)  # Kullanıcının devamsızlık sayısı
    max_absences = models.IntegerField(default=4)  # Maksimum devamsızlık hakkı

    def __str__(self):
        return f"{self.user.first_name} - {self.course_name} - Devamsızlık: {self.absences}/{self.max_absences}"


    


class QRCode(models.Model):
    academic_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)  # Ders adı
    week_info = models.CharField(max_length=50)  # Hafta bilgisi
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)  # QR kod görseli
    created_at = models.DateTimeField(auto_now_add=True)



class Course(models.Model):
    academic_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    name = models.CharField(max_length=255)  # Ders adı
    total_weeks = models.IntegerField(default=14)  # Toplam hafta sayısı
    absence_limit = models.IntegerField(default=4)  # Devamsızlık limiti
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.name} - {self.academic_user.first_name} {self.academic_user.last_name}"

class CourseStudent(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="students")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrolled_courses")
    absences = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.course.name}"
