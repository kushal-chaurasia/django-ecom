# Generated by Django 3.2.8 on 2021-10-16 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_alter_promotion_discount_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsubcategory',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.categoryproduct'),
        ),
    ]
