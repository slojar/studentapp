# Generated by Django 4.0.6 on 2022-07-27 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_delete_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='level',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='school',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
