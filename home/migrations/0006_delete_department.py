# Generated by Django 4.0.6 on 2022-07-22 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_profile_department'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Department',
        ),
    ]