# Generated by Django 5.1.3 on 2024-11-30 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='qrdata',
            name='school_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]