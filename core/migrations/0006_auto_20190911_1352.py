import core.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_auto_20190911_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todoattachmentmodel',
            name='file',
            field=models.FileField(upload_to=core.models.attachment_upload, validators=[core.models.filesize]),
        ),
    ]
