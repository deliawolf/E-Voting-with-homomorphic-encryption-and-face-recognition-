# Generated by Django 3.0.4 on 2020-10-26 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0002_auto_20201026_0645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foto',
            name='head_shot',
            field=models.ImageField(blank=True, default='profil_images/default.jpeg', upload_to='profil_images'),
        ),
    ]
