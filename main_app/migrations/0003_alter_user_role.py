# Generated by Django 5.2 on 2025-05-07 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('patient', 'patient'), ('doctor', 'doctor')], default='patient', max_length=10),
        ),
    ]
