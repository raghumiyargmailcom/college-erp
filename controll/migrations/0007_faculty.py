# Generated by Django 5.1.6 on 2025-02-23 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controll', '0006_rename_student_childrens'),
    ]

    operations = [
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('faculty_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('department', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
    ]
