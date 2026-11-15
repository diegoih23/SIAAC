from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("autenticacion", "0005_emailverificationcode"),
        ("cultivos", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="crop",
            name="assigned_users",
            field=models.ManyToManyField(
                blank=True,
                help_text="Usuarios que pueden consultar este cultivo.",
                related_name="assigned_crops",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
