from django.contrib import admin
from .models import QRData,Attendance, QRCode, Course, CourseStudent

admin.site.register(Attendance)
admin.site.register(QRCode)
admin.site.register(Course)
admin.site.register(CourseStudent)

@admin.register(QRData)
class QRDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'qr_content', 'school_number', 'date_time')
    list_filter = ('date_time',)
    search_fields = ('user__username', 'qr_content', 'school_number')