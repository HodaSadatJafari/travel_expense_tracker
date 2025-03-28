# Generated by Django 5.1.7 on 2025-03-29 10:32

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                default=django.utils.timezone.now,
                help_text="Enter your email address",
                max_length=254,
                unique=True,
                verbose_name="Email Address",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customuser",
            name="phone_number",
            field=models.CharField(
                blank=True,
                help_text="Enter your phone number (optional)",
                max_length=15,
                null=True,
                verbose_name="Phone Number",
            ),
        ),
    ]
