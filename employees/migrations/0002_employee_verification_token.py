import uuid

from django.db import migrations, models


def add_tokens(apps, schema_editor):
    Employee = apps.get_model("employees", "Employee")
    for employee in Employee.objects.filter(verification_token__isnull=True):
        employee.verification_token = uuid.uuid4()
        employee.save(update_fields=["verification_token"])


class Migration(migrations.Migration):
    dependencies = [
        ("employees", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="verification_token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True, unique=True),
        ),
        migrations.RunPython(add_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="employee",
            name="verification_token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
