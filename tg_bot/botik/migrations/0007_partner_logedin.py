# Generated by Django 5.1.1 on 2024-09-09 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botik', '0006_alter_partner_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='logedIn',
            field=models.BooleanField(default=False),
        ),
    ]
