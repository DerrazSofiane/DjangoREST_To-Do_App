from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_auto_20190911_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todomodel',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
