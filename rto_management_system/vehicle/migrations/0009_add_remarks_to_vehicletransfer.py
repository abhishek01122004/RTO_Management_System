from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0008_add_transfer_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicletransfer',
            name='remarks',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]