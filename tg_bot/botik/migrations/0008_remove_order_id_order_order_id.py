# Generated by Django 5.1.1 on 2024-09-09 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botik', '0007_partner_logedin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='id',
        ),
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
