# Generated by Django 3.2.8 on 2021-11-15 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_alter_promotion_discount_percentage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categoryproduct',
            name='image',
        ),
    ]
