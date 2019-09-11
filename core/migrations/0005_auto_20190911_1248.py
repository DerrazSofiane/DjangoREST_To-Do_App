from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_auto_20190911_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todomodel',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todos',
                                    to='core.TodoGroupModel'),
        ),
    ]
