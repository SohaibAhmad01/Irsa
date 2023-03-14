# Generated by Django 4.1.1 on 2022-11-03 08:10

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import studentmodule.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('programmodule', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(default='', max_length=255)),
                ('lastname', models.CharField(default='', max_length=255)),
                ('marital_status', models.CharField(default='', max_length=255)),
                ('cnic', models.CharField(default='', max_length=255)),
                ('phone_number', models.CharField(default='', max_length=255)),
                ('province', models.CharField(default='', max_length=255)),
                ('roll_number', models.CharField(default='', max_length=255)),
                ('address', models.CharField(default='', max_length=255)),
                ('batch', models.CharField(default='', max_length=255)),
                ('degree', models.CharField(default='', max_length=255)),
                ('dob', models.DateField()),
                ('domicile', models.CharField(default='', max_length=255)),
                ('gender', models.CharField(default='', max_length=255)),
                ('institute', models.CharField(default='', max_length=255)),
                ('image', models.ImageField(blank=True, max_length=254, null=True, upload_to=studentmodule.models.student_images)),
                ('created_at', models.DateField(default=datetime.date.today, editable=False, verbose_name='Date')),
                ('created_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='studentprogram', to='programmodule.programs')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='studentuser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
