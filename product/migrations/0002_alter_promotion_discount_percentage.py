

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotion',
            name='discount_percentage',
            field=models.DecimalField(decimal_places=2, max_digits=2),
        ),
    ]
