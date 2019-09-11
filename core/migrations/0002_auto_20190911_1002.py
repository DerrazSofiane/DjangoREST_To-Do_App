import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='todomodel',
            name='status',
            field=models.CharField(choices=[('C', 'Checked'), ('U', 'Unchecked')], default='U', max_length=1),
        ),
        migrations.CreateModel(
            name='TodoAttachmentModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=core.models.upload)),
                ('todo_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='core.TodoModel')),
            ],
        ),
    ]
