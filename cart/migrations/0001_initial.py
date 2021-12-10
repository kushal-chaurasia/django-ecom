# Generated by Django 3.2.8 on 2021-10-16 11:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Offers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('discount', models.IntegerField()),
                ('description', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('line_1', models.CharField(max_length=150)),
                ('line_2', models.CharField(blank=True, max_length=150, null=True)),
                ('landmark', models.CharField(blank=True, max_length=150, null=True)),
                ('pincode', models.CharField(max_length=10)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(blank=True, max_length=256, null=True)),
                ('status', models.IntegerField(choices=[(1, 'None'), (2, 'Pending'), (3, 'Confirmed'), (4, 'Processing'), (5, 'Delivered')], default=1)),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_refunded', models.BooleanField(default=False)),
                ('is_cancel', models.BooleanField(default=False)),
                ('order_booked', models.BooleanField(default=False)),
                ('additional_tax', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('delivery_charge', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('gross_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('offer_discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=7)),
                ('payment_method', models.IntegerField(choices=[(1, 'CASH ON DILEVERY'), (2, 'PAYTM')], default=1)),
                ('offer_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cart.offers')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('gross_weight', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.categoryproduct')),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.categoryproduct')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'product')},
            },
        ),
        migrations.CreateModel(
            name='CartProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('total', models.DecimalField(decimal_places=2, max_digits=7)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productsubcategory')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'product')},
            },
        ),
    ]
