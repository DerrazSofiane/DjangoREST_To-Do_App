import core.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_auto_20190911_1002'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='todoattachmentmodel',
            options={'ordering': ['sort']},
        ),
        migrations.AlterModelOptions(
            name='todogroupmodel',
            options={'ordering': ['sort']},
        ),
        migrations.AlterModelOptions(
            name='todomodel',
            options={'ordering': ['sort']},
        ),
        migrations.AddField(
            model_name='todoattachmentmodel',
            name='sort',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='todogroupmodel',
            name='sort',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='todomodel',
            name='sort',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='userprofilemodel',
            name='profile_photo',
            field=models.ImageField(null=True, upload_to=core.models.upload),
        ),
        migrations.AlterUniqueTogether(
            name='todoattachmentmodel',
            unique_together={('todo_item', 'sort')},
        ),
        migrations.AlterUniqueTogether(
            name='todogroupmodel',
            unique_together={('user', 'sort')},
        ),
        migrations.AlterUniqueTogether(
            name='todomodel',
            unique_together={('category', 'sort')},
        ),
    ]
