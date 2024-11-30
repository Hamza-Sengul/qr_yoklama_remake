from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

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
