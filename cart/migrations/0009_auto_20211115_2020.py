# Generated by Django 3.2.8 on 2021-11-15 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0008_offers_term_and_conditions'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.PositiveSmallIntegerField(choices=[('PENDING', 1), ('FAILED', 2), ('SUCCESS', 3), ('REFUND', 4)], default=1),
        ),
        migrations.AddField(
            model_name='order',
            name='razorpay_order_id',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
        migrations.AddField(
            model_name='order',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
        migrations.AddField(
            model_name='order',
            name='razorpay_signature',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
