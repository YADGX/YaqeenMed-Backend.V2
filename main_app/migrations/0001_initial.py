# Generated by Django 5.2 on 2025-05-07 07:30

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import main_app.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('PATIENT', 'Patient'), ('DOCTOR', 'Doctor')], default='PATIENT', max_length=10)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profiles/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png'])])),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='custom_user_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='custom_user_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('DECLINED', 'Declined'), ('COMPLETED', 'Completed')], default='PENDING', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('specialty', models.CharField(choices=[('RADIOLOGY', 'Radiology'), ('PATHOLOGY', 'Pathology'), ('CARDIOLOGY', 'Cardiology')], max_length=20)),
                ('license_number', models.CharField(max_length=50, unique=True)),
                ('years_experience', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='issue_documents/', validators=[django.core.validators.FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png']), main_app.models.validate_file_size])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='main_app.issue')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='main_app.issue')),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.PositiveIntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='patient', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.patient'),
        ),
        migrations.AddField(
            model_name='issue',
            name='doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main_app.doctor'),
        ),
        migrations.AddConstraint(
            model_name='patient',
            constraint=models.UniqueConstraint(fields=('user',), name='unique_patient_user'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['status'], name='main_app_is_status_9e4ea3_idx'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['created_at'], name='main_app_is_created_d9eb45_idx'),
        ),
    ]
