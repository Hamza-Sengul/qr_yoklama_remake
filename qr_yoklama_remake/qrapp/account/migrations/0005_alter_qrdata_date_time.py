# Generated by Django 5.1.3 on 2024-11-30 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_customuser_alter_attendance_user_alter_qrdata_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qrdata',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
