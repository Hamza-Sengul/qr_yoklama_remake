# Generated by Django 5.1.3 on 2024-11-30 15:55

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='QRData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qr_content', models.TextField()),
                ('date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qr_records', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
