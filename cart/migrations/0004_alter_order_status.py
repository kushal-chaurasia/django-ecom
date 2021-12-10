# Generated by Django 3.2.8 on 2021-10-17 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_order_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'New Order'), (2, 'Preparing'), (3, 'Ready'), (4, 'Shipped'), (5, 'Delivered')], default=1),
        ),
    ]